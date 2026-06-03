import os
import logging
from typing import List, Dict, Optional
from src.config import LLM_PROVIDER, LLM_MODEL, GROQ_API_KEY, GEMINI_API_KEY

logger = logging.getLogger(__name__)

class LLMProviderError(Exception):
    """Exception raised when LLM generation fails."""
    pass

class LLMClient:
    """Unified client for executing completions across different providers."""
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider = (provider or LLM_PROVIDER).lower()
        self.model = model or LLM_MODEL
        
    def complete(self, messages: List[Dict[str, str]], temperature: float = 0.0) -> str:
        """Runs a chat completion for the given messages."""
        logger.info(f"Running completion using provider: {self.provider}, model: {self.model}")
        
        if self.provider == "mock":
            return self._mock_complete(messages)
        elif self.provider == "groq":
            return self._groq_complete(messages, temperature)
        elif self.provider == "gemini":
            return self._gemini_complete(messages, temperature)
        else:
            logger.warning(f"Unknown provider '{self.provider}'. Falling back to mock completion.")
            return self._mock_complete(messages)
            
    def _mock_complete(self, messages: List[Dict[str, str]]) -> str:
        """Returns a simulated, safe, factual reply for testing purposes."""
        query = messages[-1]["content"].lower()
        
        # Simple rule-based mock answers matching common tests
        if "mid" in query and ("manager" in query or "who" in query):
            return (
                "Chirag Setalvad manages the HDFC Mid Cap Fund. "
                "He has been managing the fund since 2013-01-01 and has over 20 years of experience. "
                "Source: [Groww HDFC Mid-Cap Scheme Page](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth)"
            )
        elif "dhruv muchhal" in query or "manager" in query:
            return (
                "Dhruv Muchhal manages the HDFC Small Cap and HDFC Defence Funds. "
                "He holds an MBA in Finance and has over 10 years of experience in financial markets. "
                "Source: [Groww HDFC Small Cap Scheme Page](https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth)"
            )
        elif "exit load" in query:
            return (
                "The exit load of HDFC Mid-Cap Opportunities Fund is 1% if units are redeemed within 1 year of allotment. "
                "No exit load is charged after 1 year. "
                "Source: [Groww HDFC Mid-Cap Opportunities Page](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth)"
            )
        else:
            return (
                "This is a factual response from the mock LLM assistant. "
                "The target fund metrics are within normal parameters. "
                "Source: [Groww Scheme Page](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth)"
            )
            
    def _groq_complete(self, messages: List[Dict[str, str]], temperature: float) -> str:
        """Executes completion using the Groq API SDK."""
        if not GROQ_API_KEY:
            raise LLMProviderError("GROQ_API_KEY is not configured in the environment.")
            
        try:
            from groq import Groq
            client = Groq(api_key=GROQ_API_KEY)
            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=256
            )
            return completion.choices[0].message.content.strip()
        except ImportError:
            raise LLMProviderError("The 'groq' package is not installed. Please run pip install groq.")
        except Exception as e:
            logger.error(f"Groq API Error: {e}")
            raise LLMProviderError(f"Groq API completion failed: {e}")
            
    def _gemini_complete(self, messages: List[Dict[str, str]], temperature: float) -> str:
        """Executes completion using the Gemini API SDK."""
        if not GEMINI_API_KEY:
            raise LLMProviderError("GEMINI_API_KEY is not configured in the environment.")
            
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            
            # Map chat history format to Gemini roles
            contents = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({"role": role, "parts": [msg["content"]]})
                
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(
                contents,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=256
                )
            )
            return response.text.strip()
        except ImportError:
            raise LLMProviderError("The 'google-generativeai' package is not installed.")
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            raise LLMProviderError(f"Gemini API completion failed: {e}")
