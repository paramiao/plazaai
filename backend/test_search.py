import httpx
import asyncio
import json

async def test_search():
    api_key = "F7929F07-6A92-409F-86AD-EA7B3E4DE120"
    api_url = "https://api.search1api.com/search"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = [{
        "query": "深度求索公司",
        "limit": 5,
        "language": "zh-CN",
        "crawl_results": False
    }]  # 包装在列表中，使用正确的字段名
    
    print("Sending request to Search1API...")
    print(f"URL: {api_url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                api_url,
                headers=headers,
                json=data,
                timeout=30.0
            )
            
            print(f"\nResponse status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\nSuccess! Response body:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
            else:
                print(f"\nError! Response body:\n{response.text}")
                
        except Exception as e:
            print(f"\nError occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_search()) 