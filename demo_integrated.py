"""
Demostración General de Sistema (Versión Integrada).
Si abres el capó del videojuego real, así es como funciona todo el ciclo de principio a fin.
Este archivo junta y prueba todos los engranajes aislados del proyecto: 
La base de datos de conocimientos (RAG), el coordinador central (Orquestador),
la memoria del jugador y el cronómetro y logradamente nos deja echar
a rodar rápidamente una simulación artificial y compacta de juego.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuramos mágicamente las vías de acceso a las carpetas propias de tu proyecto (src) 
# subyacente para poder invocar sin líos con las dependencias locales.
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.types import Decision, ContextoEscenario, PlayerProfile
from src.orchest.uefs_orchestrator import UEFSOrchestrator
from src.utils.llm_client import create_llm_client
from src.rag.rag_client import create_rag_client

import asyncio

async def run_integrated_demo():
    print("=" * 60)
    print(" ✅ SOC TUTOR - PANEL DE DEMOSTRACIÓN GENERAL DEL FLUJO")
    print("=" * 60)
    
    # 1. Validar Conexiones al Mundo Exterior (IA)
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GROQ_API_KEY"):
        print("⚠️  Error de arranque crítico: No existe permiso local para poder enlazarse a LLMs en este PC.")
        return

    # 2. Levantar la Maquinaria Interna (Motores)
    print("\n[Inicializando motores] Encendiendo Base de datos de conocimiento a consultar (RAG) y Adaptador de la IA (LLM)...")
    llm = create_llm_client(provider="groq")
    rag = create_rag_client()
    
    doc_count = rag.count_documents()
    print(f"[Sistema RAG Inteligente] Capacidad analítica: {doc_count} documentos activos.")
    
    # 3. Llamar y asentar al Director de Orquesta de Lógica (Coordinador)
    orchestrator = UEFSOrchestrator(llm, rag)
    
    # 4. Fabricar e inyectarle un falso 'Click' virtual del usuario
    decision1 = Decision(
        accion="analizar_logs",
        target="Servidor SMTP / Global-Travel",
        detalle="Decisión: Análisis profundo de los logs del servidor SMTP tras sospecha de envío masivo accidental de datos de clientes en copia abierta (CC)."
    )
    contexto = ContextoEscenario(
        scenario_id="es-tourism-gdpr-email-breach-001",
        tipo_incidente="GDPR Data Breach (Email)",
        fase="deteccion",
        sistemas_afectados=["SMTP-Relay-01"]
    )
    perfil = PlayerProfile(player_id="marce-user", level=3)
    
    print(f"\n[Falso Escenario Jugador - Paso 1] Emitiendo Orden Oficial... '{decision1.accion}' en -> '{decision1.target}'")
    
    # 5. Pulsar "Correr" y generar toda la cadena mágica interna del Tutor Asesor
    try:
        feedback1 = await orchestrator.generar_feedback(decision1, contexto, perfil)
        
        print("\n" + "=" * 60)
        print("💡 FEEDBACK PASO 1")
        print("-" * 60)
        print(f"📊 VEREDICTO: {feedback1.evaluacion[:200]}...")
        print(f"⭐ PUNTAJE TÉCNICO: {feedback1.evaluacion_tecnica.technical_score}/100")
        print("-" * 60)

        # PASO 2: Después de ver los logs, el analista decide hacer un escaneo de red
        decision2 = Decision(
            accion="network_scan",
            target="10.0.5.0/24",
            detalle="Decisión: Escaneo de red para identificar posible movimiento lateral tras detectar accesos desde IP externa 198.51.100.15."
        )
        contexto.fase = "containment" # Avanzamos fase
        
        print(f"\n[Falso Escenario Jugador - Paso 2] Emitiendo Orden Oficial... '{decision2.accion}' en -> '{decision2.target}'")
        feedback2 = await orchestrator.generar_feedback(decision2, contexto, perfil)

        print("\n" + "=" * 60)
        print("💡 FEEDBACK PASO 2 (Complejo)")
        print("-" * 60)
        print(f"📊 VEREDICTO: {feedback2.evaluacion}")
        print(f"\n💡 EXPLICACIÓN PEDAGÓGICA: {feedback2.explicacion}")
        print(f"\n🏆 MEJOR PRÁCTICA: {feedback2.mejor_practica}")
        print(f"\n📚 FUENTES: {', '.join(feedback2.fuentes_citadas)}")
        print(f"\n⭐ PUNTAJE TÉCNICO: {feedback2.evaluacion_tecnica.technical_score}/100")
        print("-" * 60)
        
    except Exception as e:
        import traceback
        print(f"\n❌ Error en la simulación: {e}")
        traceback.print_exc()

# Ejecútate y arranca
if __name__ == "__main__":
    asyncio.run(run_integrated_demo())

