import httpx
from ..config import settings
from typing import List, Dict, Any
from fastapi import HTTPException
import logging
import json
import time

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        self.api_key = settings.SEARCH1API_KEY
        self.api_url = "https://api.search1api.com/search"
        
    async def search(self, query: str) -> Dict[str, Any]:
        """
        使用Search1API进行网络搜索
        Args:
            query: 搜索查询
        Returns:
            搜索结果和搜索参数
        """
        start_time = time.time()
        logger.info(f"[Search] Starting search for query: {query}")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        search_params = {
            "query": query,
            "max_results": 3,
            "hl": "zh-CN",
            "crawl_results": 0,
            "search_service": "google",
            "image": False
        }
        
        try:
            async with httpx.AsyncClient() as client:
                request_start = time.time()
                logger.info(f"[Search] Sending request to {self.api_url} at {request_start - start_time:.2f}s")
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=search_params,
                    timeout=10.0
                )
                request_end = time.time()
                logger.info(f"[Search] Received response in {request_end - request_start:.2f}s with status code: {response.status_code}")
                
                if response.status_code != 200:
                    error_detail = response.text
                    try:
                        error_json = response.json()
                        if isinstance(error_json, dict):
                            error_detail = error_json.get("error", {}).get("message", response.text)
                    except:
                        pass
                    
                    logger.error(f"[Search] API request failed: {error_detail}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Search API request failed: {error_detail}"
                    )
                
                try:
                    parse_start = time.time()
                    response_data = response.json()
                    
                    # 验证响应格式
                    if not isinstance(response_data, dict):
                        raise ValueError("Response data should be a dictionary")
                    
                    results = response_data.get("results", [])
                    search_parameters = response_data.get("searchParameters", search_params)
                    
                    formatted_response = {
                        "results": self._format_results(results),
                        "searchParameters": search_parameters
                    }
                    
                    end_time = time.time()
                    logger.info(f"[Search] Got {len(formatted_response['results'])} results, total time: {end_time - start_time:.2f}s")
                    return formatted_response
                    
                except json.JSONDecodeError as e:
                    logger.error(f"[Search] Failed to parse response JSON: {str(e)}")
                    logger.error(f"[Search] Response text: {response.text[:200]}...")
                    raise HTTPException(
                        status_code=500,
                        detail="Invalid JSON response from search API"
                    )
                
        except httpx.TimeoutException:
            logger.error(f"[Search] Request timed out after {time.time() - start_time:.2f}s")
            raise HTTPException(
                status_code=504,
                detail="Search request timed out"
            )
        except Exception as e:
            logger.error(f"[Search] Error during search after {time.time() - start_time:.2f}s: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred during search: {str(e)}"
            )
    
    def _format_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        格式化搜索结果
        Args:
            results: 原始搜索结果列表
        Returns:
            格式化后的搜索结果列表
        """
        try:
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "content": result.get("content", "")
                })
            return formatted_results
        except Exception as e:
            logger.error(f"Error formatting search results: {str(e)}")
            return []

search_service = SearchService() 