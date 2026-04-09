"""
Agente Analista - Evaluación técnica de decisiones con ReAct.
"""

from typing import Dict, Any, List, Optional
import json
import re

from ..agentes.types import (
    Decision, 
    ContextoEscenario, 
    EvaluacionTecnica
)
from ..agentes.prompts import REACT_PROMPT_ANALISTA
from ..utils.observability import tracer


class AgenteAnalista:
    """
    Agente Analista v2: Tool-Augmented Agent (ReAct).
    Usa herramientas para profundizar en la evaluación técnica.
    """
    
    def __init__(self, llm_client, rag_client, tools=None):
        self.llm = llm_client
        self.rag = rag_client
        self.tools = tools # SOCtools instance
    
    def evaluar(
        self, 
        decision: Decision, 
        contexto: ContextoEscenario
    ) -> EvaluacionTecnica:
        """Ejecuta la evaluación técnica usando ReAct."""
        
        # 1. Recuperar conocimiento inicial via RAG
        rag_result = self.rag.retrieve_with_context(
            decision=decision.model_dump(),
            contexto=contexto.model_dump(),
            k=3
        )
        
        contexto_rag = rag_result["contexto_rag"]
        
        # 2. Preparar ReAct
        if not self.tools:
            return self._simple_eval(decision, contexto, contexto_rag)

        tools_list = self.tools.get_tools()
        tools_desc = "\n".join([f"- {t.name}: {t.description}" for t in tools_list])
        
        prompt = REACT_PROMPT_ANALISTA.format(
            tools_desc=tools_desc,
            accion=decision.accion,
            target=decision.target,
            tipo_incidente=contexto.tipo_incidente,
            fase=contexto.fase,
            contexto_rag=contexto_rag
        )
        
        # 3. Reasoning Loop (Simplified ReAct)
        reasoning_chain = []
        max_iterations = 2
        current_prompt = prompt
        
        print(f"  [Analista] Iniciando cadena de razonamiento (ReAct)...")
        
        for i in range(max_iterations):
            response = self.llm.generate(current_prompt)
            reasoning_chain.append(response)
            
            # Buscar Acción
            action_match = re.search(r"Action: (\w+)", response)
            action_input_match = re.search(r"Action Input: (.*)", response)
            
            if action_match and action_input_match:
                action_name = action_match.group(1)
                action_input = action_input_match.group(1)
                
                print(f"    → Acción {i+1}: {action_name}('{action_input}')")
                
                # Ejecutar herramienta
                obs = "Herramienta no encontrada"
                for t in tools_list:
                    if t.name == action_name:
                        obs = t.invoke(action_input)
                        break
                
                current_prompt += f"\nObservation: {obs}\nThought: "
                tracer.add_step(f"Analista_ReAct_Step_{i}", {"action": action_name, "observation": obs})
            else:
                # No hay más acciones, buscar respuesta final
                break
        
        # 4. Extraer Final Answer
        final_answer_match = re.search(r"Final Answer: (.*)", reasoning_chain[-1], re.DOTALL)
        if final_answer_match:
            try:
                result_json = json.loads(final_answer_match.group(1).strip())
            except:
                # Intento de limpiar si falló
                cleaned = final_answer_match.group(1).strip().strip("```json").strip("```")
                try: result_json = json.loads(cleaned)
                except: result_json = {}
        else:
            # Fallback a generación directa si falló el formato ReAct
            result_json = self.llm.generate_json(f"Basado en este razonamiento, genera el JSON de evaluación: {reasoning_chain[-1]}")

        # Registrar cadena de razonamiento
        tracer.add_step("Analista_Reasoning_Chain", {"chain": reasoning_chain})

        return EvaluacionTecnica(
            fortalezas=result_json.get("fortalezas", []),
            debilidades=result_json.get("debilidades", []),
            evaluacion=result_json.get("evaluacion", "Evaluación completada con ReAct"),
            fuentes=rag_result["fuentes"] + result_json.get("fuentes", []),
            score_tecnico=result_json.get("score_tecnico", 70)
        )

    def _simple_eval(self, decision, contexto, contexto_rag) -> EvaluacionTecnica:
        """Fallback simple sin herramientas."""
        prompt = f"Evalúa esta decisión usando RAG:\n{contexto_rag}\n\nDecisión: {decision.accion}"
        result = self.llm.generate_json(prompt)
        return EvaluacionTecnica(
            fortalezas=result.get("fortalezas", []),
            debilidades=result.get("debilidades", []),
            evaluacion=result.get("evaluacion", "Evaluación simple"),
            fuentes=result.get("fuentes", []),
            score_tecnico=result.get("score_tecnico", 50)
        )