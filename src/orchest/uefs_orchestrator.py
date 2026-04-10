"""
Orquestador Principal. El engranaje número 1 que hace funcionar la "Magia" del tutor.
Este es el "Director de Orquesta" global que atiende el problema. Recibe todo lo que el 
jugador hizo dentro de tu interfaz web/juego y se encarga rigurosamente de coordinar
a quién llamar por turno (memoria, guardias de seguridad ciber, RAG o a los IAs Inspectores).
Asegura y vela por que la retroalimentación o nota final hacia el usuario nunca llegue rota, irreal o fuera de foco.
"""

from typing import Optional
import time
from datetime import datetime

# Importamos "Moldes o Maquetas de construcción" de información que aseguran 
# estructuralmente que ciertos elementos sigan reglas concretas para viajar e interactuar con facilidad por el sistema.
from ..agentes.types import (
    InputFeedbackRequest, FeedbackFinal, EvaluacionTecnica, 
    FeedbackPedagogico, ValidacionCalidad, Decision, 
    ContextoEscenario, PlayerProfile
)

# Traemos a nuestros roles Especialistas Simulados (Básicamente inteligencias especializadas en algo único).
from ..agentes.agente_analista import AgenteAnalista       # El Inspector de Reglas y riguroso.
from ..agentes.agente_explicador import AgenteExplicador   # El Maestro de escuela amigable capaz de bajar a nivel terrenal y verbal las matemáticas y normas de arriba.
from ..agentes.agente_validador import AgenteValidador     # El Auditor anti-mentiras o alucinaciones finales dictaminador de coherencia.
from ..agentes.guard_agent import GuardAgent               # El Guardia o Policía frente a ataques por prompt
from ..agentes.tools import SOCtools                       # Sus lupitas u herramientas para rascar base de datos interna.
from ..utils.memory import SessionMemory                   # La Historia a corto plazo (Libreta temporal sobre un usuario activo).
from ..utils.observability import tracer                   # El Cronómetro forense registrador.
from ..utils.semantic_cache import get_cache_client        # El 'Cerebro de Elefante' que recuerda respuestas pasadas.

class UEFSOrchestrator:
    """
    El Gran Coordinador. Ensamblador único general. Envía, recibe y verifica que la gran sinestesia del 
    mecanismo artificial se comporte de manera fluida frente a interrupciones sin caer en incoherencias.
    """
    
    def __init__(
        self,
        llm_client,
        rag_client,
        enable_validation: bool = True,
        session_id: str = "sesion-default"
    ):
        """Preparamos las credenciales e instrumentario propio del Director de orquesta al iniciar."""
        self.llm = llm_client
        self.rag = rag_client # Conexión al cofre gigante de conocimiento especializado (NIST/Mitre).
        
        # Aseguramos que el RAGClient tenga acceso al LLM para la traducción de queries
        if hasattr(self.rag, 'llm_client') and self.rag.llm_client is None:
            self.rag.llm_client = llm_client
            
        self.enable_validation = enable_validation
        self.session_id = session_id
        
        # Se instancian Componentes Base: "Okey, proveedme e inicializad mis herramientas forenses y mi libreta".
        self.tools = SOCtools(rag_client)
        self.memory = SessionMemory()
        self.guard = GuardAgent(llm_client)
        
        # "Despertamos" de la zona pasiva asíncrona uno a uno a nuestros sub-agentes de IA especializados virtuales y les repartimos acceso al conocimiento y modelos de deducción.
        self.agente_analista = AgenteAnalista(llm_client, rag_client, tools=self.tools)
        self.agente_explicador = AgenteExplicador(llm_client, rag_client)
        self.agente_validador = AgenteValidador(llm_client, rag_client)
        
        # Iniciamos el Caché Semántico (Universal English-First)
        self.cache = get_cache_client(llm_client=llm_client)
    
    def generar_feedback(
        self,
        decision: Decision,
        contexto: ContextoEscenario,
        player_profile: PlayerProfile
    ) -> FeedbackFinal:
        """
        ¡El Gran Proceso Maestro de Ingeniería! Transformar un evento humano básico "Click de Aislar" originado en tu interfaz web, en una devolución madura, contextual, gigante e inteligente.
        Esto transita sobre un carril escalonado con etapas obligatorias que son verificadas minuciosamente en cadena cronometrada.
        """
        
        # PASO CERO: Apretar el cronómetro en nuestro registro invisible (observabilidad) de forma inicial.
        tracer.start_trace("evaluacion_integral_maestra", {
            "accion": decision.accion,
            "ID de quien Juega En Vivo": self.session_id,
            "Nivel_Dificultad_Usuario": player_profile.level
        })
        
        # PASO CACHÉ: Revisar si ya respondimos algo idéntico antes para ahorrar energía y dinero.
        cached_res = self.cache.lookup(
            decision=decision.model_dump(),
            context=contexto.model_dump(),
            player_profile=player_profile.model_dump()
        )
        
        if cached_res:
             tracer.add_step("HIT_EN_CACHE_SEMANTICO", {"mensaje": "Respuesta recuperada del historial global. Saltando pipeline de agentes."})
             res = FeedbackFinal(**cached_res)
             tracer.end_trace({"Proceso": "Finalizado vía Caché"}, status="cache_hit")
             # Retornamos de inmediato el resultado guardado
             return res

        tracer.add_step("MISS_EN_CACHE_SEMANTICO", {"mensaje": "Iniciando proceso completo de análisis por IA."})
        
        # PASO 1. Módulo de Revisión Policial Virtual (Seguridad Anti-Vandalismo).
        # Revisa profundamente si lo que digitó voluntariamente el jugador es de naturaleza "normal" o si 
        # está incitando un comportamiento hostil e invasión sistémica. El Guardia virtual bloquea intentos tramposos absurdos directamente cortándoles el proceso.
        is_safe, error_msg = self.guard.validate_input(decision)
        if not is_safe:
            # Cesa la maquinaria cerrando rastros con severidad y avisa en un rebote que se interceptó vandalismo AI.
            tracer.end_trace({"error_fatal_reportado": error_msg}, status="bloqueada_debido_ataque_por_seguridad")
            raise ValueError(f"Policía Virtual IA ha abortado bruscamente todo por Riesgo de Seguridad y Normas: {error_msg}")
        
        # PASO 2. Recuperar El Pasado de Jugabilidad (Módulo de Memoria de la Partida Corta).
        # Tira de lo almacenado y recupera velozmente una recapitulación sintética enumerada donde se traza 
        # tu accionar o recorrido histórico previo como gamer, aportándole inteligencia longitudinal a la sesión de corrección para hacer un veredicto más orgánico temporalmente hablando.
        history = self.memory.get_history_summary(self.session_id)
        tracer.add_step("Lectura_De_Diarios_Previos", {"resumen_memoria_extraida": history})
        
        # PASO 3. Inyectar Revisión Ciega de Manuales Corporativos Ciber en Milisegundos (Recuperación RAG Central).
        # Aseguramos de que el Agente y sus Herramientas conozcan silenciosamente el ID exacto de este escenario (Fool-proof).
        if contexto.scenario_id:
            self.tools.set_scenario(contexto.scenario_id)

        # Buscamos en toda la memoria las pistas conectas a la "Decisión" que está en curso.
        rag_result = self.rag.retrieve_with_context(
            decision=decision.model_dump(),
            contexto=contexto.model_dump(),
            k=5 # Limitador Cuántico: Queremos que filtre selectivamente un máximo de solo los "5 extractos/párrafos" o pepitas de oro mejor ponderadas probabilísticamente por IA que hayan tocado coincidentemente dicha métrica.
        )
        tracer.add_step("Lectura_De_BasesDeDatos_NacionalesDeSeguridad", {"pdfs_descubiertos_involucrados": len(rag_result['documentos_recuperados'])})

        
        # PASO 4. Salto Cualitativo con la IA Número Uno: "El Inspector de Reglas TÉCNICO". (Pensamiento Analítico de Ciclos ReAct).
        # Pasa todos los antecedentes a una mesa donde la IA cruza minuciosamente los manuales puros versus todo el historial y accionar tuyo con los ojos de un CISO real de experiencia 
        # y da o calcula su matemática inflexible emitiendo su fallo estricto técnico (el puntaje real desnudo que sacaste sin contemplaciones).
        evaluacion_analista = self.agente_analista.evaluar(decision, contexto)
        tracer.add_step("Primer_Agente_IA_Concluye_Evaluacion_Rigurosa", {"puntaje_crudo_sin_edulcorantes": evaluacion_analista.score_tecnico})
        
        # PASO 5. Traspaso a la IA Número Dos: "Maestro de Aula / Generador Retórico Pedagógico Equilibrado".
        # Reencaucha y revalora en sus palabras toda la frialdad y abstracción devuelta que arrojó su homólogo el IA TÉCNICO y produce lo más humano e instruccional
        # que puede sacar, modificándose su tono intrínsecamente si eres catalogado Lvl 1 contra Lvl 3 Avanzado. Para Lvl bajos suaviza términos y explica que un port forwarding es, Lvl altos te trataría como oficial superior veterano.
        feedback_explicador = self.agente_explicador.generar(
            evaluacion_analista=evaluacion_analista,
            player_profile=player_profile,
            contexto_rag=rag_result["contexto_rag"] # Inserta lo oficial porque un buen tutor enseña únicamente sobre libros de texto oficiales válidos y nada se deduce del imaginario de ChatGpt abierto.
        )
        tracer.add_step("Segundo_Agente_IA_Logra_Traduccion_Contextual_Pedagogico", {})
        
        # PASO 6. Comprobación de Cruce con IA Número Tres: "Verificador Soberano de Audición y Calidad de Falsos".
        # Como medida maestra para blindar una app LLM, repasa fríamente y sin alma la coherencia interna y exactitud objetiva del discurso antes fabricado para evitar tajantemente 
        # falsedades flagrantes del anterior "Modelo" mitigando así la alucinación donde por un "despiste matemático" la IA del turno dos te hubiera sugerido "cortarle internet al CEO" sin base manual alguna.
        validacion = self.agente_validador.validar(
            evaluacion_analista=evaluacion_analista,
            feedback_explicador=feedback_explicador,
            player_profile=player_profile,
            contexto_rag=rag_result["contexto_rag"]
        )
        
        # PASO 7. Cierre Documentario: Agendamos solemnemente el evento victorioso dentro de la libretita o sesión permanente o efímera en la computadora misma, garantizando que conste la procedencia.
        self.memory.save_step(self.session_id, {
            "decision": decision.model_dump(),
            "timestamp": datetime.now().isoformat() # Huella del tiempo oficial atómico que certifica formal la carga.
        })
        
        # PASO 8. Sellado Final: Unifica todo para mandarle a tu código frontend Web (Angular/React, etc) en formato ordenado la estructura final que se pinchará hacia el panel tuyo de la vista para poder visibilizar.
        res = FeedbackFinal(
            evaluacion=feedback_explicador.evaluacion,
            explicacion=feedback_explicador.explicacion,
            mejor_practica=feedback_explicador.mejor_practica,
            fuentes_citadas=rag_result["fuentes"] + feedback_explicador.fuentes_citadas,
            evaluacion_tecnica=evaluacion_analista,
            validacion=validacion,
            costo_estimado=0.0006 # Simulador imaginario fijo calculado de cuántos céntimos de dólares acabaría cobrándote google real en tokens si usamos API Enterprise con tal volumen de texto global arrojado.
        )
        
        # PASO REGISTRO EN CACHE: Guardamos este nuevo conocimiento para que otros (o tú mismo) se beneficien después.
        self.cache.store(
            decision=decision.model_dump(),
            context=contexto.model_dump(),
            player_profile=player_profile.model_dump(),
            feedback=res
        )
        
        # Detener la contabilidad de latencia al terminar milisegundos tras esta entrega veloz general.
        tracer.end_trace({"Proceso Total Macro Completado": "Exitosamente Sin Trabadas."})
        
        # Se escupe tu paquete integral devuelto, todo hecho un genio pulido desde la máquina.
        return res