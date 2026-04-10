"""
Analyst Agent - Technical evaluation of decisions using ReAct.
Internal reasoning is performed in English to optimize token costs and consistency.
"""

from typing import Dict, Any, List, Optional
import json
import re

from ..agentes.types import (
    Decision, 
    ContextoEscenario, 
    EvaluacionTecnica
)
from ..agentes.prompts import REACT_PROMPT_ANALISTA, build_prompt_analista
from ..utils.observability import tracer


class AgenteAnalista:
    """
    Analyst Agent v2: Tool-Augmented Agent (ReAct).
    Uses tools to deepen technical evaluation.
    Internal reasoning is conducted in English.
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
        """Executes technical evaluation using ReAct in English."""
        
        # 1. Retrieve initial knowledge via RAG (Automatic English translation if needed)
        rag_result = self.rag.retrieve_with_context(
            decision=decision.model_dump(),
            contexto=contexto.model_dump(),
            k=3
        )
        
        contexto_rag = rag_result["contexto_rag"]
        
        # 2. Prepare ReAct
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
        
        print(f"  [Analyst] Starting reasoning chain (ReAct in English)...")
        
        for i in range(max_iterations):
            response = self.llm.generate(current_prompt)
            reasoning_chain.append(response)
            
            # Search for Action in English
            action_match = re.search(r"Action: (\w+)", response)
            action_input_match = re.search(r"Action Input: (.*)", response)
            
            if action_match and action_input_match:
                action_name = action_match.group(1).strip()
                action_input = action_input_match.group(1).strip()
                
                print(f"    → Action {i+1}: {action_name}('{action_input}')")
                
                # Execute tool
                obs = "Tool not found"
                for t in tools_list:
                    if t.name == action_name:
                        obs = t.invoke(action_input)
                        break
                
                current_prompt += f"\nObservation: {obs}\nThought: "
                tracer.add_step(f"Analyst_ReAct_Step_{i}", {"action": action_name, "observation": obs})
            else:
                # No more actions, look for final answer
                break
        
        # 4. Extract Final Answer
        final_answer_match = re.search(r"Final Answer: (.*)", reasoning_chain[-1], re.DOTALL)
        if final_answer_match:
            try:
                result_json = json.loads(final_answer_match.group(1).strip())
            except:
                # Attempt to clean if JSON parsing failed
                cleaned = final_answer_match.group(1).strip().strip("```json").strip("```")
                try: result_json = json.loads(cleaned)
                except: result_json = {}
        else:
            # Fallback to direct generation if ReAct format failed
            result_json = self.llm.generate_json(f"Based on this technical reasoning, generate the evaluation JSON: {reasoning_chain[-1]}")
        
        tracer.add_step("Analyst_Reasoning_Chain", {"chain": reasoning_chain})

        return EvaluacionTecnica(
            fortalezas=result_json.get("fortalezas", []),
            debilidades=result_json.get("debilidades", []),
            evaluacion=result_json.get("evaluacion", "Evaluation completed via English reasoning loop"),
            fuentes=rag_result["fuentes"] + result_json.get("fuentes", []),
            score_tecnico=result_json.get("score_tecnico", 70)
        )

    def _simple_eval(self, decision: Decision, contexto: ContextoEscenario, contexto_rag: str) -> EvaluacionTecnica:
        """Simple fallback without tools, using English prompts."""
        prompt = build_prompt_analista(
            decision=decision.model_dump(),
            contexto=contexto.model_dump(),
            contexto_rag=contexto_rag
        )
        result = self.llm.generate_json(prompt)
        
        return EvaluacionTecnica(
            fortalezas=result.get("fortalezas", []),
            debilidades=result.get("debilidades", []),
            evaluacion=result.get("evaluacion", "Direct evaluation"),
            fuentes=result.get("fuentes", []),
            score_tecnico=result.get("score_tecnico", 50)
        )