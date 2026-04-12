import unittest
from unittest.mock import MagicMock
from src.orchest.uefs_orchestrator import UEFSOrchestrator
from src.agents.types import Decision, ContextoEscenario, PlayerProfile

class TestUEFSPipeline(unittest.TestCase):
    
    def setUp(self):
        # Mock de clientes para no gastar tokens ni requerir Chroma en CI
        self.mock_llm = MagicMock()
        self.mock_rag = MagicMock()
        
        # Simular respuestas
        self.mock_rag.retrieve_with_context.return_value = {
            "contexto_rag": "Fake RAG info",
            "documentos_recuperados": [],
            "fuentes": ["NIST"]
        }
        
        # Setup orquestador
        self.orchestrator = UEFSOrchestrator(
            llm_client=self.mock_llm,
            rag_client=self.mock_rag,
            enable_validation=False # Simplificar para integration basic
        )

    def test_full_flow_simplificado(self):
        # Mock de la evaluación técnica
        self.orchestrator.agente_analista.evaluar = MagicMock(return_value=MagicMock(score_tecnico=85, fuentes=["NIST"]))
        self.orchestrator.agente_explicador.generar = MagicMock(return_value=MagicMock(
            evaluacion="Bien hecho", 
            explicacion="...", 
            mejor_practica="...", 
            fuentes_citadas=[]
        ))
        
        decision = Decision(accion="bloquear", target="IP")
        contexto = ContextoEscenario(tipo_incidente="phishing", fase="contencion")
        perfil = PlayerProfile(player_id="test", level=1)
        
        feedback = self.orchestrator.generar_feedback(decision, contexto, perfil)
        
        self.assertEqual(feedback.evaluacion_tecnica.score_tecnico, 85)
        self.mock_rag.retrieve_with_context.assert_called()

if __name__ == "__main__":
    unittest.main()
