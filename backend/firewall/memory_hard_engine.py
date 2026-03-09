

"""
Real Memory-Hard Engine using Argon2id
Industry-standard password hashing function
Resistant to GPU/ASIC attacks due to memory requirements
"""

import secrets
import time
from dataclasses import dataclass, asdict
from typing import Tuple

try:
    from argon2 import PasswordHasher
    from argon2.low_level import hash_secret_raw, Type
    ARGON2_AVAILABLE = True
except ImportError:
    ARGON2_AVAILABLE = False
    print("Warning: argon2-cffi not available, using fallback")
    import hashlib

from backend.config import settings
from backend.utils.logger import logger


@dataclass
class MemoryHardChallenge:
    """Real Argon2 memory-hard challenge"""
    salt: str                
    time_cost: int          
    memory_cost: int        
    parallelism: int        
    hash_length: int        
    target_prefix: str      
    nonce: str             
    timestamp: int         
    client_ip: str
    
    def to_dict(self):
        data = asdict(self)
        del data['client_ip']
        return data


class MemoryHardEngine:
    """
    Real Memory-Hard Challenge using Argon2id
    
    Argon2 won the Password Hashing Competition (2015)
    
    Security Properties:
    - Memory-bound: Requires large RAM allocation
    - GPU-resistant: Memory bandwidth bottleneck
    - ASIC-resistant: Custom hardware economically infeasible
    - Tunable: Adjust time/memory/parallelism independently
    
    Argon2id = Hybrid mode (combines Argon2i + Argon2d)
    - Argon2i: Data-independent (side-channel resistant)
    - Argon2d: Data-dependent (maximum resistance to time-memory tradeoffs)
    """
    
    def __init__(self):
        self.memory_cost = settings.MEMORY_COST    
        self.time_cost = settings.TIME_COST        
        self.parallelism = settings.PARALLELISM    
        self.hash_length = 32                      
        self.timeout = 120
        self.use_argon2 = ARGON2_AVAILABLE
        
        
        self.difficulty_bytes = 1
        
        logger.info(f"Memory-Hard Engine initialized - "
                   f"Memory: {self.memory_cost/1024:.1f}MB, "
                   f"Time: {self.time_cost} iterations, "
                   f"Parallelism: {self.parallelism}, "
                   f"Argon2: {self.use_argon2}")
    
    def generate_challenge(self, client_ip: str,
                          suspicious_level: int = 0) -> MemoryHardChallenge:
        """
        Generate memory-hard challenge
        
        Args:
            client_ip: Client's IP
            suspicious_level: 0-10 (increases difficulty)
        """
        
        salt = secrets.token_bytes(16)
        
        
        time_cost = self.time_cost
        memory_cost = self.memory_cost
        difficulty_bytes = self.difficulty_bytes
        
        if suspicious_level > 0:
            
            time_cost = min(self.time_cost + suspicious_level, 10)
            memory_cost = min(
                self.memory_cost * (1 + suspicious_level // 3),
                262144  
            )
            difficulty_bytes = min(
                self.difficulty_bytes + suspicious_level // 4,
                4  
            )
        
        target_prefix = "0" * (difficulty_bytes * 2)  
        
        challenge = MemoryHardChallenge(
            salt=salt.hex(),
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=self.parallelism,
            hash_length=self.hash_length,
            target_prefix=target_prefix,
            nonce=secrets.token_hex(16),
            timestamp=int(time.time()),
            client_ip=client_ip
        )
        
        logger.info(f"Memory-Hard challenge for {client_ip}: "
                   f"Memory={memory_cost/1024:.1f}MB, "
                   f"Time={time_cost}, "
                   f"Target={target_prefix}")
        
        return challenge
    
    def solve_challenge(self, challenge: MemoryHardChallenge,
                       max_attempts: int = 100000) -> Tuple[str, int]:
        """
        CLIENT-SIDE: Solve memory-hard challenge
        
        Find input that produces Argon2 hash with required prefix
        This requires allocating memory_cost KiB of RAM
        """
        salt = bytes.fromhex(challenge.salt)
        
        logger.info(f"Solving Memory-Hard challenge - "
                   f"Target: {challenge.target_prefix}")
        start_time = time.time()
        
        attempt = 0
        while attempt < max_attempts:
            
            candidate = f"{challenge.nonce}:{attempt}".encode()
            
            try:
                if self.use_argon2:
                    
                    hash_result = hash_secret_raw(
                        secret=candidate,
                        salt=salt,
                        time_cost=challenge.time_cost,
                        memory_cost=challenge.memory_cost,
                        parallelism=challenge.parallelism,
                        hash_len=challenge.hash_length,
                        type=Type.ID  
                    )
                else:
                    
                    hash_result = hashlib.sha256(salt + candidate).digest()
                
                hash_hex = hash_result.hex()
                
                
                if hash_hex.startswith(challenge.target_prefix):
                    solve_time = time.time() - start_time
                    logger.info(f"Memory-Hard solved: {attempt} attempts in "
                               f"{solve_time:.2f}s - Hash: {hash_hex[:16]}...")
                    return candidate.decode(), attempt
                
                
                if attempt % 1000 == 0 and attempt > 0:
                    elapsed = time.time() - start_time
                    rate = attempt / elapsed
                    logger.debug(f"Memory-Hard progress: {attempt} attempts "
                                f"({rate:.1f} attempts/s)")
                
            except Exception as e:
                logger.error(f"Argon2 computation error: {e}")
                raise
            
            attempt += 1
        
        raise Exception(f"Solution not found in {max_attempts} attempts")
    
    def verify_solution(self, challenge: MemoryHardChallenge,
                       solution: str) -> Tuple[bool, str]:
        """
        SERVER-SIDE: Verify memory-hard solution
        
        Note: Argon2 verification requires same computation as solving
        (unlike VDF where verification is faster)
        This is acceptable because GPUs/ASICs can't optimize it anyway
        """
        
        if time.time() - challenge.timestamp > self.timeout:
            return False, "Challenge expired"
        
        try:
            salt = bytes.fromhex(challenge.salt)
            
            logger.debug(f"Verifying Memory-Hard solution: {solution[:32]}...")
            
            if self.use_argon2:
                
                hash_result = hash_secret_raw(
                    secret=solution.encode(),
                    salt=salt,
                    time_cost=challenge.time_cost,
                    memory_cost=challenge.memory_cost,
                    parallelism=challenge.parallelism,
                    hash_len=challenge.hash_length,
                    type=Type.ID
                )
            else:
                
                hash_result = hashlib.sha256(salt + solution.encode()).digest()
            
            hash_hex = hash_result.hex()
            
            
            if hash_hex.startswith(challenge.target_prefix):
                logger.info(f"Memory-Hard verification PASSED - "
                           f"Hash: {hash_hex[:16]}...")
                return True, "Memory-hard challenge verified"
            else:
                logger.warning(f"Memory-Hard verification FAILED - "
                              f"Expected: {challenge.target_prefix}, "
                              f"Got: {hash_hex[:len(challenge.target_prefix)]}")
                return False, "Hash prefix mismatch"
                
        except Exception as e:
            logger.error(f"Memory-Hard verification error: {e}")
            return False, f"Verification error: {str(e)}"
    
    def estimate_memory_usage(self, memory_cost: int) -> str:
        """Human-readable memory usage"""
        mb = memory_cost / 1024
        if mb >= 1024:
            return f"{mb/1024:.1f} GB"
        return f"{mb:.1f} MB"



memory_hard_engine = MemoryHardEngine()
