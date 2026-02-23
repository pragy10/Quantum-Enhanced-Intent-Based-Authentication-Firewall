# File: attack_simulations/reset_limits.py

import redis
import sys

try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    # Clear all rate limit and verification keys
    deleted = 0
    for key in r.scan_iter("rate_limit:*"):
        r.delete(key)
        deleted += 1
    
    for key in r.scan_iter("vdf_verified:*"):
        r.delete(key)
        deleted += 1
        
    for key in r.scan_iter("memory_verified:*"):
        r.delete(key)
        deleted += 1
    
    print(f"✅ Cleared {deleted} rate limit/verification keys!")
    print("You can now test smart bot with clean slate.\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Make sure Redis is running!")
    sys.exit(1)
