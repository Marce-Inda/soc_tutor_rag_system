import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.llm_client import LLMClient
from src.rag.rag_client import RAGClient
from src.orchest.uefs_orchestrator import UEFSOrchestrator
from src.agents.types import Decision, ContextoEscenario, PlayerProfile

async def test_e2e_nvidia_flow():
    load_dotenv()
    
    print("\n--- 🕵️ PROEBA END-TO-END: ORQUESTADOR CON VALIDADOR NVIDIA ---")
    
    # 1. Inicializar Clientes
    # Principal: Gemini (Rápido)
    llm_main = LLMClient(provider="gemini")
    
    # Validador: NVIDIA NIM Llama-3.3-70B (Alta Precisión)
    if not os.getenv("NVIDIA_API_KEY"):
        print("❌ ERROR: NVIDIA_API_KEY no encontrada en .env")
        return
        
    llm_validator = LLMClient(provider="nvidia", model="meta/llama-3.3-70b-instruct")
    
    # RAG
    rag = RAGClient()
    
    # 2. Inicializar Orquestador
    orchestrator = UEFSOrchestrator(
        llm_client=llm_main,
        rag_client=rag,
        validator_llm_client=llm_validator
    )
    
    # 3. Datos de Prueba (Simulación de Phishing)
    test_decision = Decision(
        accion="Bloquear la dirección IP del remitente en el Firewall perimetral",
        target="192.168.1.100",
        detalle="La IP ha enviado 500 correos de phishing en 10 minutos. Es una medida reactiva necesaria."
    )
    
    test_contexto = ContextoEscenario(
        tipo_incidente="phishing",
        fase="containment",
        sistemas_afectados=["Email Gateway", "Firewall"],
        scenario_id="phishing_campaign_01",
        dificultad="intermedio"
    )
    
    test_profile = PlayerProfile(
        player_id="test_user_nvidia",
        level=3,
        rol="analyst",
        language="es",
        dilema_index_session=1
    )
    
    print("\n[Orchestrator] Generando feedback... (Esto invocará a Gemini y finalmente a NVIDIA)")
    
    try:
        feedback = await orchestrator.generar_feedback(
            decision=test_decision,
            contexto=test_contexto,
            player_profile=test_profile
        )
        
        print("\n" + "="*50)
        print("📊 RESULTADO DEL FEEDBACK")
        print("="*50)
        print(f"✅ Evaluación: {feedback.evaluacion}")
        print(f"📖 Explicación: {feedback.explicacion[:200]}...")
        print(f"🛡️ Validado por: {feedback.validacion.model_used if hasattr(feedback.validacion, 'model_used') else 'NVIDIA NIM'}")
        print(f"💎 Consistencia Técnica: {'APROBADA' if feedback.validacion.approved else 'RECHAZADA'}")
        print(f"📉 Costo Estimado: ${feedback.costo_estimado:.5f}")
        print(f"⏱️ Latencia: {feedback.latencia_ms:.2f} ms")
        print("="*50)
        
        if feedback.validacion.approved:
            print("\n🎉 ¡ÉXITO! El flujo completo con NVIDIA como Validador Supremo funciona.")
        else:
            print("\n⚠️ El Validador de NVIDIA detectó inconsistencias en el análisis (esto es bueno, demuestra su rigor técnico).")
            
    except Exception as e:
        import traceback
        print(f"\n❌ FALLO EN EL FLUJO E2E:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_e2e_nvidia_flow())
