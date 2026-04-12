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

# Configuramos mágicamente las vías de acceso a las carpetas propias de tu proyecto (src) 
# subyacente para poder invocar sin líos con las dependencias locales.
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.types import Decision, ContextoEscenario, PlayerProfile
from src.orchest.uefs_orchestrator import UEFSOrchestrator
from src.utils.llm_client import create_llm_client
from src.rag.rag_client import create_rag_client

def run_integrated_demo():
    print("=" * 60)
    print(" ✅ SOC TUTOR - PANEL DE DEMOSTRACIÓN GENERAL DEL FLUJO")
    print("=" * 60)
    
    # 1. Validar Conexiones al Mundo Exterior (IA)
    # Validamos que tu computadora tenga activas las famosas 'API Keys' virtuales. Sin estas claves maestras no nos permitirán interactuar 
    # con los poderosos pero costosos modelos hospedados en la nube como Google, OpenAI o la plataforma Groq.
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GROQ_API_KEY"):
        print("⚠️  Error de arranque crítico: No existe permiso local para poder enlazarse a LLMs en este PC (Faltan variables GEMINI_API_KEY o GROQ_API_KEY).")
        return

    # 2. Levantar la Maquinaria Interna (Motores)
    print("\n[Inicializando motores] Encendiendo Base de datos de conocimiento a consultar (RAG) y Adaptador de la IA (LLM)...")
    llm = create_llm_client(provider="gemini") # Habilitaremos la mente de Google Flash como piloto principal por el instante.
    rag = create_rag_client() # Invoca e inspecciona la enciclopedia guardada.
    
    # Efectuamos un veloz cruce para certificar que el archivista no está inútil antes de proseguir el simulacro y de esta forma no gastar cuotas mal.
    doc_count = rag.count_documents()
    print(f"[Sistema RAG Inteligente] Hay en custodia actualmente una capacidad analítica en la memoria de alrededor de: {doc_count} páginas/documentos activos para cotejar.")
    
    # 3. Llamar y asentar al Director de Orquesta de Lógica (Coordinador)
    # Ahora que lo demás prendió, mandamos empoderar al jefe central, asignándole a su gestión ambas partes (Base de datos Local + Cerebro en Nube) 
    # e intencionalmente se simula su registro bajo nombre de seguimiento "demo-session-001".
    orchestrator = UEFSOrchestrator(llm, rag, session_id="sesion-artificial-demo-001")
    
    # 4. Fabricar e inyectarle un falso 'Click' virtual del usuario
    # Como no estamos detrás del cliente o la pantalla en este modo tester, 
    # fingimos programáticamente un suceso donde un Analista detectó que se vulneraba la red:
    decision = Decision(
        accion="aislar_host",
        target="WORKSTATION-X",
        detalle="Decisión: Aislamiento severo del nodo informático originado por rastro fehaciente de múltiples ejecuciones de PowerShell anómalas."
    )
    # Le alimentamos también datos periféricos simulados desde los tableros al supervisor Orquestador:
    contexto = ContextoEscenario(
        tipo_incidente="ransomware", # Virus extorsivo a la red
        fase="deteccion",
        sistemas_afectados=["WORKSTATION-X"]
    )
    # Especificamos sus aptitudes para poder proveer adecuadamente la crítica a medida
    perfil = PlayerProfile(player_id="marce-user", level=2) # Nivel Principiante (Lvl 2)
    
    print(f"\n[Falso Escenario Jugador] Emitiendo Orden Oficial hacia la máquina... '{decision.accion}' bajo la mira en dispositivo -> '{decision.target}'")
    print(f"[Nervio Orquestador] Analizando el proceder y emitiendo un juicio justo y educativo con nuestros agents...")
    
    # 5. Pulsar "Correr" y generar toda la cadena mágica interna del Tutor Asesor
    try:
        # El Orquestador junta nuestras variables inventadas de arriba y arranca un engranaje extenso de evaluación en varios frentes simultáneos (Seguridad > Memoria > RAG > ReAct)
        feedback = orchestrator.generar_feedback(decision, contexto, perfil)
        
        # ¡Magia! Imprime por fin en letras clarísimas y amigables el resultado para presentar a los usuarios o monitores del front.
        print("\n" + "=" * 60)
        print("💡 FEEDBACK EN CASO DE ÉXITO FINAL")
        print("-" * 60)
        print(f"📊 VEREDICTO EVALUATORIO DEL JUEZ: {feedback.evaluacion}")
        print(f"\n💡 TRADUCCIÓN SIMPLIFICADA PEDAGÓGICA (Del Experto IA Explicador): {feedback.explicacion}")
        print(f"\n🏆 INSTRUCCIÓN MANUAL BASADA EN NIST: {feedback.mejor_practica}")
        print(f"\n📚 DOCUMENTACIÓN O SUSTENTO LEGAL DEL RAG: {', '.join(feedback.fuentes_citadas)}")
        print(f"\n⭐ PUNTAJE OBTENIDO (SISTEMA CRUDO Y NUMERADO): {feedback.evaluacion_tecnica.score_tecnico}/100 Puntos a tu bolsa")
        print("-" * 60)
        
        # Comentarios finales en torno a auditorías de backoffice
        print(f"\n[Auditoria Total y Silenciosa] La constancia métrica del funcionamiento IA bajó y se archivó sin que nadie note a los registros de rastreo traces/..")
        print(f"[Recordatorio para Próximo Jugador] La presente ronda de respuesta está ahora resguardada bajo los historiales de '{orchestrator.session_id}' en memoria corta persistente.")
        
    except Exception as e:
        print(f"\n❌ Se produjo alguna alerta o cortocircuito parando toda la simulación: {e}")

# Ejecútate y arranca obligatoriamente si abro al demo puntualmente con mi terminal.
if __name__ == "__main__":
    run_integrated_demo()
