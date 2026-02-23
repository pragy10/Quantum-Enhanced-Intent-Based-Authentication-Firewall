# File: test_step3_rate_limit.py

import httpx
import asyncio

API_URL = "http://127.0.0.1:8000/protected"

async def main():
    print("\n=== Testing Rate Limiter (Step 3) ===\n")
    async with httpx.AsyncClient() as client:
        success = 0
        blocked = 0
        for i in range(1, 121):
            r = await client.get(API_URL)
            if r.status_code == 200:
                success += 1
            elif r.status_code == 429:
                blocked += 1
            print(f"Request {i}: {r.status_code}")

        print(f"\nTotal success: {success}")
        print(f"Total blocked: {blocked}\n")

if __name__ == "__main__":
    asyncio.run(main())
