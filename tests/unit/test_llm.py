import unittest
from unittest.mock import MagicMock, patch
from src.utils.llm_client import LLMClient

class TestLLMClient(unittest.TestCase):
    
    @patch('src.utils.llm_client.LANGCHAIN_AVAILABLE', True)
    def test_provider_initialization(self):
        # Test que el cliente se inicializa con el proveedor correcto
        client = LLMClient(provider="ollama")
        self.assertEqual(client.get_provider(), "ollama")

    @patch('src.utils.llm_client.LLMClient.generate')
    def test_generate_json(self, mock_generate):
        mock_generate.return_value = '{"fortalezas": ["test"], "score_tecnico": 90}'
        
        client = LLMClient()
        result = client.generate_json("test prompt")
        
        self.assertEqual(result["score_tecnico"], 90)
        self.assertIn("test", result["fortalezas"])

if __name__ == "__main__":
    unittest.main()
