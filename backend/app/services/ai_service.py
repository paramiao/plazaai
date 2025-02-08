import httpx
from ..config import settings
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
import logging
import json
import time

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_key = settings.SILICONFLOW_API_KEY
        self.base_url = "https://api.siliconflow.com/v1"
        
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        Get available models from SiliconFlow API
        Returns:
            List of available models and their details
        """
        logger.info("Getting models list from SiliconFlow API")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    error_detail = response.json().get("error", {}).get("message", response.text)
                    logger.error(f"Failed to get models list: {error_detail}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"API request failed: {error_detail}"
                    )
                
                models = response.json()
                logger.info(f"Successfully got {len(models.get('data', []))} models")
                return models
                
        except httpx.TimeoutException:
            logger.error("Timeout while fetching models list")
            raise HTTPException(
                status_code=504,
                detail="Request timeout while fetching models list."
            )
        except Exception as e:
            logger.error(f"Error fetching models: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while fetching models: {str(e)}"
            )
        
    async def get_ai_response(
        self,
        messages: List[Dict[str, str]],
        model_name: Optional[str] = None
    ) -> str:
        """
        Get response from SiliconFlow API
        Args:
            messages: List of message objects
            model_name: Name of the model to use
        Returns:
            AI response text
        """
        start_time = time.time()
        logger.info(f"[AI] Starting request using model: {model_name or settings.DEFAULT_MODEL}")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_name or settings.DEFAULT_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000,
            "stream": False
        }
        
        logger.info(f"[AI] Request payload size: {len(json.dumps(payload))} bytes")
        
        try:
            logger.info(f"[AI] Sending request to {self.base_url}/chat/completions")
            request_start = time.time()
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=180.0
                )
                request_end = time.time()
                logger.info(f"[AI] Received response in {request_end - request_start:.2f}s with status code: {response.status_code}")
                logger.info(f"[AI] Response headers: {dict(response.headers)}")
                
                if response.status_code != 200:
                    error_detail = response.text
                    try:
                        error_json = response.json()
                        if isinstance(error_json, dict):
                            error_detail = error_json.get("error", {}).get("message", response.text)
                    except:
                        pass
                    
                    logger.error(f"[AI] API request failed: {error_detail}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"API request failed: {error_detail}"
                    )
                
                try:
                    parse_start = time.time()
                    result = response.json()
                    logger.info("[AI] Successfully parsed response JSON")
                    content = result["choices"][0]["message"]["content"]
                    end_time = time.time()
                    logger.info(f"[AI] Response length: {len(content)} chars, total time: {end_time - start_time:.2f}s")
                    return content
                except Exception as e:
                    logger.error(f"[AI] Failed to parse response JSON: {str(e)}")
                    logger.error(f"[AI] Response text: {response.text[:200]}...")
                    raise HTTPException(
                        status_code=500,
                        detail="Invalid JSON response from AI API"
                    )
                
        except httpx.TimeoutException:
            logger.error(f"[AI] Request timed out after {time.time() - start_time:.2f}s")
            raise HTTPException(
                status_code=504,
                detail="Request timeout. The model is taking too long to respond."
            )
        except Exception as e:
            logger.error(f"[AI] Error after {time.time() - start_time:.2f}s: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred: {str(e)}"
            )

ai_service = AIService() 