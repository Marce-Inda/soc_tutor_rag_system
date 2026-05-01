"""
Token Counter Utility - SOC Tutor.
Handles token counting and cost estimation for different LLM providers.
"""

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
from typing import Dict, Any

# Precios por 1M de tokens (Precios representativos mayo 2026)
# Estos valores deben actualizarse según el mercado.
PRICING = {
    "gemini": {
        "input": 0.15,  # USD per 1M tokens (Gemini 2.5 Flash)
        "output": 0.60
    },
    "groq": {
        "input": 0.50, # Llama 3 70B
        "output": 0.80
    },
    "deepseek": {
        "input": 0.14,  # DeepSeek V4 Flash — el más barato del mercado
        "output": 0.28
    },
    "ollama": {
        "input": 0.0,
        "output": 0.0
    }
}

class TokenCounter:
    """Utility to estimate costs and count tokens."""
    
    @staticmethod
    def count_tokens(text: str, model: str = "gpt-4") -> int:
        """
        Counts tokens using tiktoken with a Circuit Breaker fallback.
        """
        try:
            if not TIKTOKEN_AVAILABLE:
                raise ImportError("tiktoken not installed")
            # Intentamos usar el encoding de OpenAI
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except Exception as e:
            # CIRCUIT BREAKER: Si tiktoken falla (memoria, red, errores de paquete),
            # degradamos a una estimación estable de 4 caracteres por token.
            print(f"  [TokenCounter] Circuit Breaker activated: {e}. Using character-based estimation.")
            return max(1, len(text) // 4)

    @staticmethod
    def estimate_cost(input_tokens: int, output_tokens: int, provider: str) -> float:
        """Estimates cost based on provider pricing."""
        prices = PRICING.get(provider, {"input": 0.0, "output": 0.0})
        
        input_cost = (input_tokens / 1_000_000) * prices["input"]
        output_cost = (output_tokens / 1_000_000) * prices["output"]
        
        return input_cost + output_cost
