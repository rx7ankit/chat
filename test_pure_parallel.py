import json
import asyncio
import aiohttp
import time

async def send_request(session, prompt_id, prompt_text):
    """Send one request - pure and simple"""
    start_time = time.time()
    
    try:
        async with session.post(
            "http://localhost:8000/chat",
            json={"message": prompt_text}
        ) as response:
            result = await response.json()
            end_time = time.time()
            
            response_text = result.get('response', str(result))
            request_time = end_time - start_time
            
            print(f"✅ Prompt {prompt_id}: {request_time:.1f}s")
            return prompt_id, response_text, request_time
            
    except Exception as e:
        end_time = time.time()
        request_time = end_time - start_time
        print(f"❌ Prompt {prompt_id}: {request_time:.1f}s - {str(e)}")
        return prompt_id, f"Error: {str(e)}", request_time

async def main():
    """Pure parallel execution - no limits, no delays"""
    
    # Load prompts
    with open('prompt.json', 'r', encoding='utf-8') as f:
        prompts = json.load(f)
    
    print(f"🚀 Testing {len(prompts)} prompts with PURE parallelism")
    print("=" * 60)
    
    # NO CONNECTION LIMITS - Maximum parallelism
    connector = aiohttp.TCPConnector(
        limit=0,           # Unlimited total connections
        limit_per_host=0,  # Unlimited per-host connections
        ttl_dns_cache=300,
        use_dns_cache=True
    )
    
    # Extended timeout for individual requests
    timeout = aiohttp.ClientTimeout(total=600)  # 10 minutes per request
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        start_time = time.time()
        
        # Create ALL tasks at once - true parallelism
        tasks = [
            send_request(session, prompt_id, prompt_text)
            for prompt_id, prompt_text in prompts.items()
        ]
        
        print(f"📊 Created {len(tasks)} tasks - executing ALL simultaneously...")
        
        # Execute ALL at once
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Process results
        answers = {}
        successful = 0
        failed = 0
        times = []
        
        for result in results:
            if isinstance(result, Exception):
                failed += 1
            else:
                prompt_id, response_text, request_time = result
                answers[prompt_id] = response_text
                times.append(request_time)
                if "Error" not in response_text:
                    successful += 1
                else:
                    failed += 1
        
        # Save results
        with open('answer.json', 'w', encoding='utf-8') as f:
            json.dump(answers, f, indent=2, ensure_ascii=False)
        
        # Show results
        print("\n" + "=" * 60)
        print("🎯 PURE PARALLELISM RESULTS")
        print("=" * 60)
        print(f"Total prompts: {len(prompts)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total time: {total_time:.1f} seconds")
        
        if times:
            print(f"Fastest response: {min(times):.1f}s")
            print(f"Slowest response: {max(times):.1f}s")
            print(f"Average response: {sum(times)/len(times):.1f}s")
            
            # The key metric: parallelism efficiency
            theoretical_time = min(times)  # If truly parallel, total = fastest
            efficiency = (theoretical_time / total_time) * 100
            print(f"🔥 Parallelism efficiency: {efficiency:.1f}%")
            
            if efficiency > 90:
                print("🎉 EXCELLENT! True parallelism achieved!")
            elif efficiency > 70:
                print("✅ GOOD! Near-parallel execution")
            else:
                print("⚠️ BOTTLENECK! Parallelism needs improvement")
        
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
