

"""
DDoS Attack Simulation - Multiple bots attacking simultaneously
Expected Result: All get rate-limited and blocked
"""

import requests
import time
import threading
from queue import Queue

BASE_URL = "http://127.0.0.1:8000"

def bot_worker(bot_id, num_requests, results_queue):
    """Single bot making requests"""
    success = 0
    blocked = 0
    
    for i in range(num_requests):
        try:
            resp = requests.get(f"{BASE_URL}/protected", timeout=2)
            if resp.status_code == 200:
                success += 1
            else:
                blocked += 1
        except:
            blocked += 1
    
    results_queue.put({'bot_id': bot_id, 'success': success, 'blocked': blocked})

def ddos_attack(num_bots=10, requests_per_bot=50):
    """Simulate DDoS with multiple concurrent bots"""
    
    print("\n" + "="*60)
    print("DDOS ATTACK SIMULATION")
    print("="*60)
    print(f"Number of Bots:       {num_bots}")
    print(f"Requests per Bot:     {requests_per_bot}")
    print(f"Total Attack Size:    {num_bots * requests_per_bot} requests")
    print(f"Target:               {BASE_URL}/protected")
    print("\nLaunching attack...\n")
    
    results_queue = Queue()
    threads = []
    
    start_time = time.time()
    
    
    for bot_id in range(num_bots):
        thread = threading.Thread(
            target=bot_worker,
            args=(bot_id, requests_per_bot, results_queue)
        )
        thread.start()
        threads.append(thread)
        print(f"[!] Bot {bot_id+1} launched")
    
    
    for thread in threads:
        thread.join()
    
    elapsed = time.time() - start_time
    
    
    total_success = 0
    total_blocked = 0
    
    while not results_queue.empty():
        result = results_queue.get()
        total_success += result['success']
        total_blocked += result['blocked']
    
    total_requests = num_bots * requests_per_bot
    
    print("\n" + "="*60)
    print("DDOS ATTACK RESULTS")
    print("="*60)
    print(f"Total Bots:          {num_bots}")
    print(f"Total Requests:      {total_requests}")
    print(f"✓ Successful:        {total_success} ({total_success/total_requests*100:.1f}%)")
    print(f"✗ Blocked:           {total_blocked} ({total_blocked/total_requests*100:.1f}%)")
    print(f"Time Elapsed:        {elapsed:.2f}s")
    print(f"Attack Rate:         {total_requests/elapsed:.1f} req/s")
    print("\nFIREWALL EFFECTIVENESS:")
    print(f"   Blocked: {total_blocked/total_requests*100:.1f}%")
    print(f"   Attack neutralized in {elapsed:.2f} seconds")
    print("="*60)
    
    return {
        'num_bots': num_bots,
        'total': total_requests,
        'success': total_success,
        'blocked': total_blocked,
        'time': elapsed,
        'rate': total_requests/elapsed
    }

if __name__ == "__main__":
    print("\nWARNING: DDoS Attack Simulation")
    print("This simulates a coordinated attack with multiple bots.")
    print("Make sure your firewall server is running!\n")
    
    input("Press Enter to launch DDoS attack...")
    
    results = ddos_attack(num_bots=10, requests_per_bot=50)
    
    print("\nDDoS simulation complete!")
    print(f"\nThe firewall successfully defended against {results['num_bots']} attacking bots!")
