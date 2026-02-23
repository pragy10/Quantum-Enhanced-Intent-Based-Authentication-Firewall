

"""
Simple Bot Attack - Attempts to flood the server
Expected Result: Blocked by rate limiting after 100 requests
"""

import requests
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def simple_bot_attack(num_requests=200):
    """Spam requests without solving challenges"""
    
    print("\n" + "="*60)
    print("SIMPLE BOT ATTACK - No Challenge Solving")
    print("="*60)
    print(f"Target: {BASE_URL}/protected")
    print(f"Attack size: {num_requests} requests")
    print(f"Strategy: Brute force flood\n")
    
    success_count = 0
    blocked_count = 0
    error_count = 0
    
    start_time = time.time()
    
    for i in range(1, num_requests + 1):
        try:
            response = requests.get(f"{BASE_URL}/protected", timeout=2)
            
            if response.status_code == 200:
                success_count += 1
                status = "✓ SUCCESS"
            elif response.status_code == 429:
                blocked_count += 1
                status = "✗ RATE LIMITED"
            elif response.status_code == 403:
                blocked_count += 1
                status = "✗ BLOCKED (No Token)"
            else:
                error_count += 1
                status = f"? ERROR ({response.status_code})"
            
            if i % 10 == 0 or blocked_count == 1:
                print(f"Request {i:3d}: {status}")
                
        except requests.exceptions.Timeout:
            error_count += 1
            print(f"Request {i:3d}: ✗ TIMEOUT")
        except Exception as e:
            error_count += 1
            print(f"Request {i:3d}: ✗ ERROR - {e}")
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*60)
    print("ATTACK RESULTS")
    print("="*60)
    print(f"Total Requests:  {num_requests}")
    print(f"✓ Successful:    {success_count} ({success_count/num_requests*100:.1f}%)")
    print(f"✗ Blocked:       {blocked_count} ({blocked_count/num_requests*100:.1f}%)")
    print(f"? Errors:        {error_count}")
    print(f"Time Elapsed:    {elapsed:.2f}s")
    print(f"Request Rate:    {num_requests/elapsed:.1f} req/s")
    print("="*60)
    
    return {
        'total': num_requests,
        'success': success_count,
        'blocked': blocked_count,
        'errors': error_count,
        'time': elapsed,
        'rate': num_requests/elapsed
    }

if __name__ == "__main__":
    print("\nStarting Simple Bot Attack Simulation...")
    print("Make sure your firewall server is running!\n")
    
    input("Press Enter to start attack...")
    
    results = simple_bot_attack(200)
    
    print("\nSimulation complete!")
    print(f"\nFirewall blocked {results['blocked']/results['total']*100:.1f}% of attack requests!")
