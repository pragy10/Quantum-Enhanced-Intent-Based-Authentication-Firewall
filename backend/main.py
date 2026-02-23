from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import secrets
import time
from typing import Dict, Any, List, Union

from config import settings
from utils.logger import logger
from utils.redis_client import RedisClient
from firewall.rate_limiter import RateLimiter
from firewall.vdf_engine import vdf_engine, VDFChallenge
from firewall.memory_hard_engine import memory_hard_engine, MemoryHardChallenge
from firewall.quantum_engine import quantum_engine


class VDFSolution(BaseModel):
    challenge_nonce: str 
    solution: Union[int, str]
    proof_chain: List[Union[int, str]] 

class MemoryHardSolution(BaseModel):
    challenge_nonce: str
    solution: str

class QuantumSolution(BaseModel):
    challenge: str
    simulate_tamper: bool = False

class IntentVerification(BaseModel):
    vdf_challenge_nonce: str
    vdf_solution: VDFSolution
    memory_challenge_nonce: str
    memory_solution: MemoryHardSolution


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

redis_client = RedisClient()
rate_limiter = RateLimiter(redis_client)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Your Vite React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    allowed = await rate_limiter.check_rate_limit(client_ip)
    
    if not allowed:
        return rate_limiter.get_block_response(client_ip)
    
    response = await call_next(request)
    return response



@app.get("/")
async def root():
    return {
        "message": "Intent-Based Firewall - Hybrid Crypto Edition",
        "features": [
            "Rate Limiting ✅",
            "VDF Challenge ✅", 
            "Memory-Hard Challenge ✅",
            "Hybrid Verification ✅"
        ]
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "redis_connected": redis_client.ping(),
        "rate_limiter": {
            "max_requests": settings.RATE_LIMIT_REQUESTS,
            "window_seconds": settings.RATE_LIMIT_WINDOW
        },
        "crypto_challenges": {
            "vdf_enabled": settings.VDF_ENABLED,
            "memory_hard_enabled": settings.MEMORY_HARD_ENABLED
        }
    }


@app.get("/challenge/vdf")
async def get_vdf_challenge(request: Request):
    """Get VDF challenge"""
    client_ip = request.client.host
    challenge = vdf_engine.generate_challenge(client_ip)
    
    import json
    redis_client.set_with_expiry(
        f"vdf_challenge:{challenge.nonce}",
        json.dumps(challenge.to_dict()),  # ← Convert to JSON string
        vdf_engine.timeout
    )
    
    
    return {
        "type": "vdf",
        "challenge": challenge.to_dict(),
        "estimated_solve_time": "2-5 seconds",
        "message": "Compute sequential proof chain"
    }


# File: main.py (update verify_vdf_solution)

# File: main.py (verify_vdf_solution function)

@app.post("/challenge/vdf/verify")
async def verify_vdf_solution(solution: VDFSolution, request: Request):
    """Verify VDF solution"""
    client_ip = request.client.host
    
    challenge_key = f"vdf_challenge:{solution.challenge_nonce}"
    challenge_json = redis_client.get(challenge_key)
    
    if not challenge_json:
        logger.warning(f"VDF challenge not found: {solution.challenge_nonce}")
        raise HTTPException(400, "No matching challenge found or challenge expired")
    
    import json
    challenge_dict = json.loads(challenge_json) if isinstance(challenge_json, str) else challenge_json
    
    from backend.firewall.vdf_engine import VDFChallenge
    
    # CRITICAL FIX: Convert base back to int when reconstructing
    challenge = VDFChallenge(
        modulus=challenge_dict['modulus'],
        base=int(challenge_dict['base']),  # ← CONVERT TO INT!
        time_parameter=challenge_dict['time_parameter'],
        nonce=challenge_dict['nonce'],
        timestamp=challenge_dict['timestamp'],
        difficulty_level=challenge_dict.get('difficulty_level', 1),
        client_ip=client_ip
    )
    
    # Convert proof chain from strings to integers
    try:
        solution_int = int(solution.solution) if isinstance(solution.solution, str) else solution.solution
        proof_chain_ints = [int(p) if isinstance(p, str) else p for p in solution.proof_chain]
        
        # DEBUG LOG
        logger.info(f"Challenge base (int): {challenge.base}")
        logger.info(f"Proof chain[0] (int): {proof_chain_ints[0]}")
        logger.info(f"Are they equal? {challenge.base == proof_chain_ints[0]}")
        
    except ValueError as e:
        logger.error(f"Invalid number format in solution: {e}")
        raise HTTPException(400, "Invalid solution format")
    
    is_valid, message = vdf_engine.verify_solution(
        challenge, solution_int, proof_chain_ints
    )
    
    if is_valid:
        token = secrets.token_hex(32)
        redis_client.set_with_expiry(f"vdf_verified:{client_ip}", token, 600)
        redis_client.delete(challenge_key)
        
        return {"verified": True, "token": token, "message": message}
    else:
        raise HTTPException(403, message)




@app.get("/challenge/memory-hard")
async def get_memory_hard_challenge(request: Request):
    """Get Memory-Hard challenge"""
    client_ip = request.client.host
    challenge = memory_hard_engine.generate_challenge(client_ip)
    
    import json
    redis_client.set_with_expiry(
        f"memory_challenge:{challenge.nonce}",
        json.dumps(challenge.to_dict()),  # ← Convert to JSON string
        memory_hard_engine.timeout
    )
    
    return {
        "type": "memory-hard",
        "challenge": challenge.to_dict(),
        "estimated_solve_time": "1-3 seconds",
        "memory_required": f"{challenge.memory_cost/1024:.1f} MB",
        "message": "Find input producing hash with required prefix"
    }



# File: main.py (replace verify_memory_hard_solution AGAIN)

@app.post("/challenge/memory-hard/verify")
async def verify_memory_hard_solution(solution: MemoryHardSolution, request: Request):
    """Verify Memory-Hard solution"""
    client_ip = request.client.host
    
    # Get stored challenge using nonce
    challenge_key = f"memory_challenge:{solution.challenge_nonce}"
    challenge_json = redis_client.get(challenge_key)
    
    if not challenge_json:
        logger.warning(f"Memory-Hard challenge not found: {solution.challenge_nonce}")
        raise HTTPException(400, "No matching challenge found or challenge expired")
    
    # Parse challenge data
    import json
    import hashlib
    challenge_dict = json.loads(challenge_json) if isinstance(challenge_json, str) else challenge_json
    
    # Reconstruct MemoryHardChallenge
    from backend.firewall.memory_hard_engine import MemoryHardChallenge
    challenge = MemoryHardChallenge(
        salt=challenge_dict['salt'],
        time_cost=challenge_dict['time_cost'],
        memory_cost=challenge_dict['memory_cost'],
        parallelism=challenge_dict['parallelism'],
        hash_length=challenge_dict['hash_length'],
        target_prefix=challenge_dict['target_prefix'],
        nonce=challenge_dict['nonce'],
        timestamp=challenge_dict['timestamp'],
        client_ip=client_ip
    )
    
    # Check timestamp
    if time.time() - challenge.timestamp > memory_hard_engine.timeout:
        raise HTTPException(403, "Challenge expired")
    
    # ===== MATCH JAVASCRIPT ALGORITHM EXACTLY =====
    try:
        logger.debug(f"Verifying Memory-Hard solution: {solution.solution[:40]}...")
        
        # First hash: hash the solution string (returns hex)
        hash_result = hashlib.sha256(solution.solution.encode()).hexdigest()
        
        # Chain 100 hashes (hashing hex strings, not bytes!)
        for i in range(1000):
            hash_result = hashlib.sha256(hash_result.encode()).hexdigest()
        
        # Final hash (one more time)
        final_hash = hashlib.sha256(hash_result.encode()).hexdigest()
        
        logger.info(f"Server computed hash: {final_hash}")
        logger.info(f"Target prefix: {challenge.target_prefix}")
        
        # Verify prefix requirement
        if final_hash.startswith(challenge.target_prefix):
            token = secrets.token_hex(32)
            redis_client.set_with_expiry(f"memory_verified:{client_ip}", token, 600)
            
            # Clean up challenge
            redis_client.delete(challenge_key)
            
            logger.info(f"[SUCCESS] Memory-Hard verification PASSED - Hash: {final_hash[:16]}...")
            return {
                "verified": True, 
                "token": token, 
                "message": "Memory-hard challenge verified"
            }
        else:
            logger.warning(f"[FAILED] Hash mismatch - Expected prefix: {challenge.target_prefix}, Got: {final_hash[:len(challenge.target_prefix)]}")
            raise HTTPException(403, f"Hash prefix mismatch. Expected: {challenge.target_prefix}, Got: {final_hash[:8]}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Memory-Hard verification error: {e}")
        raise HTTPException(500, f"Verification error: {str(e)}")


@app.get("/challenge/quantum")
async def get_quantum_challenge(request: Request):
    """Get Layer 2 Quantum challenge. Requires Layer 1 completion."""
    client_ip = request.client.host
    
    # Enforce progressive defense: Layer 1 must be passed first
    vdf_token = redis_client.get(f"vdf_verified:{client_ip}")
    memory_token = redis_client.get(f"memory_verified:{client_ip}")
    if not vdf_token or not memory_token:
        raise HTTPException(403, "Layer 1 Resource Barriers must be passed first.")
        
    challenge = quantum_engine.get_challenge()
    redis_client.set_with_expiry(f"quantum_challenge:{client_ip}", challenge, 120)
    
    return {
        "type": "quantum", 
        "challenge": challenge, 
        "message": "Encode challenge into quantum circuit phase"
    }

@app.post("/challenge/quantum/verify")
async def verify_quantum_solution(solution: QuantumSolution, request: Request):
    """Verify Layer 2: Quantum Entanglement Correlation"""
    client_ip = request.client.host
    
    # Retrieve the stored challenge for this IP
    stored_challenge = redis_client.get(f"quantum_challenge:{client_ip}")
    if not stored_challenge or stored_challenge != solution.challenge:
        raise HTTPException(400, "Invalid or expired quantum challenge")

    # Run the PennyLane quantum circuit authentication
    is_valid, fidelity = quantum_engine.authenticate_client(solution.challenge, solution.simulate_tamper)
    
    if is_valid:
        final_token = secrets.token_hex(32)
        # 3600 seconds = 1-Hour Access Token
        redis_client.set_with_expiry(f"quantum_verified:{client_ip}", final_token, 3600) 
        redis_client.delete(f"quantum_challenge:{client_ip}") # Clean up
        
        return {
            "verified": True, 
            "token": final_token, 
            "fidelity": fidelity, 
            "message": "Quantum Bell-State Entanglement Verified."
        }
    else:
        logger.warning(f"Quantum tamper detected for {client_ip}. Fidelity: {fidelity}")
        raise HTTPException(403, "Quantum Authentication Failed — Tampering Detected")

# File: main.py (replace /protected endpoint)

@app.get("/protected")
async def protected_data(request: Request):
    """Protected endpoint - REQUIRES final Quantum verification token"""
    client_ip = request.client.host
    
    # Check for the final Layer 2 token
    quantum_token = redis_client.get(f"quantum_verified:{client_ip}")
    
    if quantum_token:
        logger.info(f"[SUCCESS] Access granted to {client_ip} - all layers verified")
        return {
            "status": "access_granted",
            "message": "Sensitive research data unlocked",
            "data": {
                "classification": "TOP SECRET",
                "project": "Quantum Authentication Research",
                "timestamp": time.time(),
                "confidential_payload": "XJ-99 Aerospace Schematics Unlocked."
            }
        }
    else:
        logger.warning(f"[FAILED] Access denied to {client_ip} - Missing Quantum Token")
        raise HTTPException(
            status_code=403, 
            detail="Intent verification incomplete. Quantum authentication required."
        )

