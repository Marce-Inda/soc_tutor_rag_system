import unittest
import shutil
import os
from pathlib import Path
from src.rag.rag_client import RAGClient

class TestRAGClient(unittest.TestCase):
    def setUp(self):
        # Usar un directorio temporal para el test
        self.tmp_dir = "tests/tmp_chroma"
        self.client = RAGClient(persist_directory=self.tmp_dir, collection_name="test-collection")
        
    def tearDown(self):
        # Limpiar después de los tests
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_add_and_count(self):
        docs = [
            {"text": "NIST 800-61 es para respuesta a incidentes", "source": "nist"},
            {"text": "MITRE T1071 es Application Layer Protocol", "source": "mitre"}
        ]
        self.client.add_documents(docs)
        self.assertEqual(self.client.count_documents(), 2)

    def test_retrieve(self):
        docs = [{"text": "Phishing detection guide", "source": "nist"}]
        self.client.add_documents(docs)
        
        results = self.client.retrieve("phishing", k=1)
        self.assertEqual(len(results), 1)
        self.assertIn("Phishing", results[0]["text"])

if __name__ == "__main__":
    unittest.main()
