

"""
Smart Bot Attack - Attempts to solve cryptographic challenges
Expected Result: Takes too long, economically infeasible at scale
"""

import requests
import time
import hashlib

BASE_URL = "http://127.0.0.1:5000"

def solve_vdf_simplified(challenge):
    """Simplified VDF solver (slower than browser)"""
    modulus = int(challenge['modulus'])
    base = int(challenge['base'])
    time_param = challenge['time_parameter']
    
    result = base % modulus
    proof_chain = [str(result)]
    
    
    for i in range(time_param):
        result = pow(result, 2, modulus)
        if (i + 1) % 1000 == 0:
            proof_chain.append(str(result))
    
    if proof_chain[-1] != str(result):
        proof_chain.append(str(result))
    
    return {
        'solution': str(result),
        'proof_chain': proof_chain
    }

def solve_memory_hard_simplified(challenge):
    """Simplified memory-hard solver"""
    salt = challenge['salt']
    target_prefix = challenge['target_prefix']
    
    attempt = 0
    while attempt < 50000:
        candidate = f"{salt}:{attempt}"
        
        
        hash_result = hashlib.sha256(candidate.encode()).hexdigest()
        for _ in range(100):
            hash_result = hashlib.sha256(hash_result.encode()).hexdigest()
        
        final_hash = hashlib.sha256(hash_result.encode()).hexdigest()
        
        if final_hash.startswith(target_prefix):
            return candidate
        
        attempt += 1
    
    raise Exception("Could not solve memory-hard challenge")

def smart_bot_attack(num_attempts=10):
    """Bot that tries to solve challenges"""
    
    print("\n" + "="*60)
    print("SMART BOT ATTACK - With Challenge Solving")
    print("="*60)
    print(f"Target: {BASE_URL}/protected")
    print(f"Attack size: {num_attempts} authenticated requests")
    print(f"Strategy: Solve crypto challenges for each request\n")
    
    success_count = 0
    failed_count = 0
    total_solve_time = 0
    
    overall_start = time.time()
    
    for i in range(1, num_attempts + 1):
        print(f"\n--- Attempt {i}/{num_attempts} ---")
        attempt_start = time.time()
        
        try:
            
            print("  Getting VDF challenge...")
            resp = requests.get(f"{BASE_URL}/challenge/vdf", timeout=5)
            
            if resp.status_code == 429:
                print(f"  ✗ Rate limited! Bot blocked.")
                failed_count += 1
                continue
            
            if resp.status_code != 200:
                print(f"  ✗ Failed to get challenge (status {resp.status_code})")
                failed_count += 1
                continue
            
            data = resp.json()
            if 'challenge' not in data:
                print(f"  ✗ Invalid response: {data}")
                failed_count += 1
                continue
                
            vdf_challenge = data['challenge']
            
            
            print("  Solving VDF (this takes ~5 seconds)...")
            vdf_start = time.time()
            vdf_solution = solve_vdf_simplified(vdf_challenge)
            vdf_time = time.time() - vdf_start
            print(f"  ✓ VDF solved in {vdf_time:.2f}s")
            
            
            verify_resp = requests.post(
                f"{BASE_URL}/challenge/vdf/verify",
                json={
                    'challenge_nonce': vdf_challenge['nonce'],
                    'solution': vdf_solution['solution'],
                    'proof_chain': vdf_solution['proof_chain']
                }
            )
            
            if verify_resp.status_code != 200:
                print(f"  ✗ VDF verification failed")
                failed_count += 1
                continue
            
            print("  ✓ VDF verified")
            
            
            print("  Getting Memory-Hard challenge...")
            resp = requests.get(f"{BASE_URL}/challenge/memory-hard")
            mem_challenge = resp.json()['challenge']
            
            
            print("  Solving Memory-Hard (this takes ~2 seconds)...")
            mem_start = time.time()
            mem_solution = solve_memory_hard_simplified(mem_challenge)
            mem_time = time.time() - mem_start
            print(f"  ✓ Memory-Hard solved in {mem_time:.2f}s")
            
            
            verify_resp = requests.post(
                f"{BASE_URL}/challenge/memory-hard/verify",
                json={
                    'challenge_nonce': mem_challenge['nonce'],
                    'solution': mem_solution
                }
            )
            
            if verify_resp.status_code != 200:
                print(f"  ✗ Memory-Hard verification failed")
                failed_count += 1
                continue
            
            print("  ✓ Memory-Hard verified")
            
            
            data_resp = requests.get(f"{BASE_URL}/protected")
            if data_resp.status_code == 200:
                attempt_time = time.time() - attempt_start
                total_solve_time += attempt_time
                success_count += 1
                print(f" ACCESS GRANTED (took {attempt_time:.2f}s total)")
            else:
                failed_count += 1
                print(f"  ✗ Access denied")
                
        except Exception as e:
            failed_count += 1
            print(f"  ✗ ERROR: {e}")
    
    overall_time = time.time() - overall_start
    avg_time_per_request = total_solve_time / success_count if success_count > 0 else 0
    
    print("\n" + "="*60)
    print("SMART BOT ATTACK RESULTS")
    print("="*60)
    print(f"Total Attempts:       {num_attempts}")
    print(f"✓ Successful:         {success_count}")
    print(f"✗ Failed:             {failed_count}")
    print(f"Total Time:           {overall_time:.2f}s")
    print(f"Avg Time/Request:     {avg_time_per_request:.2f}s")
    print(f"Effective Rate:       {success_count/overall_time:.3f} req/s")
    print("\nAnalysis:")
    print(f"   To make 1000 requests: ~{avg_time_per_request * 1000 / 60:.1f} minutes")
    print(f"   To make 10000 requests: ~{avg_time_per_request * 10000 / 3600:.1f} hours")
    print(f"   DDoS of 10000 req/s: Would need {10000 * avg_time_per_request:.0f} parallel bots!")
    print("="*60)
    
    return {
        'total': num_attempts,
        'success': success_count,
        'failed': failed_count,
        'total_time': overall_time,
        'avg_time': avg_time_per_request,
        'rate': success_count/overall_time if overall_time > 0 else 0
    }

if __name__ == "__main__":
    print("\nStarting Smart Bot Attack Simulation...")
    print("This will take ~70 seconds for 10 attempts (7s each)")
    print("Make sure your firewall server is running!\n")
    
    input("Press Enter to start attack...")
    
    results = smart_bot_attack(5)  
    
    print("\nSimulation complete!")
    print(f"\nEven a 'smart' bot can only make {results['rate']:.3f} req/s!")
    print(f"    A DDoS needs 1000+ req/s - this bot is 1000x too slow!")
