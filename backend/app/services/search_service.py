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
        self.api_url = "https://api.search1api.com/search"  # 使用正确的API端点
        
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """
        使用Search1API进行网络搜索
        Args:
            query: 搜索查询
        Returns:
            搜索结果列表
        """
        start_time = time.time()
        logger.info(f"[Search] Starting search for query: {query}")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = [{
            "query": query,
            "limit": 3,
            "language": "zh-CN",
            "crawl_results": False
        }]
        
        try:
            async with httpx.AsyncClient() as client:
                request_start = time.time()
                logger.info(f"[Search] Sending request to {self.api_url} at {request_start - start_time:.2f}s")
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=data,
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
                    results = response.json()
                    if isinstance(results, list) and len(results) > 0:
                        search_results = results[0].get("results", [])
                        formatted_results = self._format_results({"results": search_results})
                        end_time = time.time()
                        logger.info(f"[Search] Got {len(formatted_results)} results, total time: {end_time - start_time:.2f}s")
                        return formatted_results
                    return []
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
    
    def _format_results(self, raw_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        格式化原始搜索结果
        Args:
            raw_results: 原始API响应
        Returns:
            格式化后的搜索结果列表
        """
        try:
            formatted_results = []
            results = raw_results.get("results", [])
            if not results and isinstance(raw_results, list):
                results = raw_results
                
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "url": result.get("link", result.get("url", ""))  # 使用link作为url
                })
            return formatted_results
        except Exception as e:
            logger.error(f"Error formatting search results: {str(e)}")
            return []

search_service = SearchService() 