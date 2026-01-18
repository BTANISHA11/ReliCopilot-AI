"""Ollama LLM agent for failure analysis."""

import httpx
from typing import Optional
from config import OLLAMA_BASE_URL, OLLAMA_MODEL


class OllamaAgent:
    """Agent for analyzing failures using local Ollama LLM."""
    
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def analyze_failure(
        self, 
        error_message: str, 
        endpoint: str, 
        status_code: int,
        context: Optional[str] = None
    ) -> str:
        """
        Analyze a failure using the LLM.
        
        Args:
            error_message: The error message to analyze
            endpoint: The endpoint where the error occurred
            status_code: HTTP status code
            context: Additional context about the error
            
        Returns:
            Analysis string from the LLM
        """
        prompt = self._build_prompt(error_message, endpoint, status_code, context)
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Unable to generate analysis")
            else:
                return f"Ollama API error: {response.status_code}"
                
        except httpx.ConnectError:
            return "Ollama not available. Install Ollama and run: ollama pull llama2"
        except Exception as e:
            return f"Analysis error: {str(e)}"
    
    def _build_prompt(
        self, 
        error_message: str, 
        endpoint: str, 
        status_code: int,
        context: Optional[str]
    ) -> str:
        """Build the prompt for the LLM."""
        prompt = f"""You are an AI reliability engineer analyzing a system failure.

Endpoint: {endpoint}
Status Code: {status_code}
Error Message: {error_message}
"""
        if context:
            prompt += f"Additional Context: {context}\n"
        
        prompt += """
Please provide:
1. Root cause analysis
2. Potential impact
3. Recommended remediation steps

Keep the analysis concise and actionable (max 150 words)."""
        
        return prompt
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
