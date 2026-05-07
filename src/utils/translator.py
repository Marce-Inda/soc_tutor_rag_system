import logging
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)

class Translator:
    """
    Utility for high-speed, deterministic translations using the LLMClient.
    Optimized for the English-First Reasoning Gateway.
    """
    
    def __init__(self, llm_client: Any):
        self.llm = llm_client
        # Session cache to avoid redundant translations of common terms or identical inputs
        self._cache: Dict[str, str] = {}

    async def translate_to_english(self, text: str) -> str:
        """
        Translates Spanish/Portuguese input to English for internal processing.
        """
        if not text or text.strip() == "":
            return text
            
        if text in self._cache:
            return self._cache[text]
            
        system_prompt = (
            "You are a high-speed translation microservice. "
            "Translate the following SOC analyst input to English concisely. "
            "Maintain technical IDs and proper names exactly."
        )
        
        try:
            translation = await self.llm.generate(f"Translate to English: {text}", system_prompt=system_prompt)
            result = translation.strip()
            self._cache[text] = result
            return result
        except Exception as e:
            logger.warning(f"Translation to English failed: {e}")
            return text

    async def translate_to_user_language(self, text: str, target_language: str) -> str:
        """
        Translates final English reasoning back to the user's preferred language.
        """
        if not text or not text.strip() or not target_language or target_language == "en":
            return text
            
        system_prompt = (
            f"You are a professional technical translator specializing in cybersecurity. "
            f"Translate the following text into {target_language}. "
            f"RULES: "
            f"1. Maintain a professional, pedagogical, and technical tone. "
            f"2. Keep technical IDs, IP addresses, hashes, and entity names (NIST, MITRE, GDPR) exactly as they are. "
            f"3. Return ONLY the translated text. DO NOT add any comments like 'Here is the translation' or 'The text is already in...'. "
            f"4. If the text is already in {target_language}, return the input text verbatim."
        )
        
        try:
            translation = await self.llm.generate(text, system_prompt=system_prompt)
            return translation.strip()
        except Exception as e:
            logger.error(f"Translation to {target_language} failed: {e}")
            return text

    async def translate_batch(self, texts: list[str], target_language: str) -> list[str]:
        """
        Translates a list of strings in a single LLM call to save tokens and time.
        """
        if not texts or target_language == "en":
            return texts
            
        # Filter empty strings
        filtered_texts = [t for t in texts if t and t.strip()]
        if not filtered_texts:
            return texts

        system_prompt = (
            f"You are an expert technical translator. Translate this JSON list of cybersecurity "
            f"observations to {target_language}. Return ONLY a JSON list of strings."
        )
        
        try:
            prompt = f"Translate this list: {texts}"
            result_json = await self.llm.generate_json(prompt, system_prompt=system_prompt)
            if isinstance(result_json, list):
                return result_json
            return texts
        except Exception as e:
            logger.error(f"Batch translation to {target_language} failed: {e}")
            return texts
