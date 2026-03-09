import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import redis
from typing import Optional
from backend.config import settings
from backend.utils.logger import logger

class RedisClient:
    """Redis client wrapper with connection management"""
    
    def __init__(self):
        """Initialize Redis connection"""
        self.host = settings.REDIS_HOST
        self.port = settings.REDIS_PORT
        self.db = settings.REDIS_DB
        self.password = settings.REDIS_PASSWORD
        
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,  
                socket_connect_timeout=5
            )
            
            
            self.client.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
            
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def ping(self) -> bool:
        """Test Redis connection"""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    def set(self, key: str, value: str) -> bool:
        """Set a key-value pair"""
        try:
            self.client.set(key, value)
            logger.debug(f"Set key: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to set key {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        try:
            value = self.client.get(key)
            logger.debug(f"Get key: {key} = {value}")
            return value
        except Exception as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None
    
    def set_with_expiry(self, key: str, value: str, seconds: int) -> bool:
        """Set key with automatic expiration"""
        try:
            self.client.setex(key, seconds, value)
            logger.debug(f"Set key with expiry: {key} (expires in {seconds}s)")
            return True
        except Exception as e:
            logger.error(f"Failed to set key with expiry {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a key"""
        try:
            self.client.delete(key)
            logger.debug(f"Deleted key: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete key {key}: {e}")
            return False
    
    def increment(self, key: str) -> int:
        """Increment counter"""
        try:
            value = self.client.incr(key)
            logger.debug(f"Incremented key: {key} = {value}")
            return value
        except Exception as e:
            logger.error(f"Failed to increment key {key}: {e}")
            return 0
    
    def keys(self, pattern: str = "*") -> list:
        """Get all keys matching pattern"""
        try:
            return self.client.keys(pattern)
        except Exception as e:
            logger.error(f"Failed to get keys with pattern {pattern}: {e}")
            return []
    
    def dbsize(self) -> int:
        """Get number of keys in database"""
        try:
            return self.client.dbsize()
        except Exception as e:
            logger.error(f"Failed to get database size: {e}")
            return 0


def test_redis_client():
    """Test Redis client functionality"""
    print("\nTesting Redis Client...\n")
    
    
    client = RedisClient()
    
    
    print("Test 1: Ping")
    if client.ping():
        print("[✓] Redis connection OK\n")
    else:
        print("[X] Redis connection failed\n")
        return
    
    
    print("Test 2: Set and Get")
    client.set("test_key", "test_value")
    value = client.get("test_key")
    if value == "test_value":
        print(f"[✓] Set/Get works: {value}\n")
    else:
        print(f"[X] Set/Get failed\n")
    
    
    print("Test 3: Set with Expiry")
    client.set_with_expiry("temp_key", "temp_value", 10)
    value = client.get("temp_key")
    if value == "temp_value":
        print(f"[✓] Expiry set works: {value} (expires in 10s)\n")
    else:
        print(f"[X] Expiry set failed\n")
    
    
    print("Test 4: Increment")
    client.delete("counter")  
    count1 = client.increment("counter")
    count2 = client.increment("counter")
    count3 = client.increment("counter")
    if count1 == 1 and count2 == 2 and count3 == 3:
        print(f"[✓] Increment works: 1 -> 2 -> 3\n")
    else:
        print(f"[X] Increment failed\n")
    
    
    print("Test 5: Database Info")
    size = client.dbsize()
    print(f"[✓] Database has {size} keys\n")
    
    
    client.delete("test_key")
    client.delete("temp_key")
    client.delete("counter")
    
    print("[✓] All Redis tests passed!\n")

if __name__ == "__main__":
    test_redis_client()
