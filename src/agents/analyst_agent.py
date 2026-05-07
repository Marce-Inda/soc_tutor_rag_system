"""
Analyst Agent - Technical evaluation of decisions using ReAct.
Internal reasoning is performed in English to optimize token costs and consistency.
"""

# ## AGENTE ANALISTA v2
# Este agente utiliza el patrón ReAct (Razonamiento + Acción) para investigar incidencias.



from typing import Dict, Any, List, Optional
import json
import re

from ..agents.types import (
    Decision, 
    ContextoEscenario, 
    EvaluacionTecnica
)
from ..agents.prompts import REACT_PROMPT_ANALISTA, build_prompt_analista
from ..utils.observability import tracer


class AnalystAgent:

    """
    Analyst Agent: Tool-augmented agent for deep technical investigation.
    """


    
    def __init__(self, llm_client, rag_client, tools=None):
        self.llm = llm_client
        self.rag = rag_client
        self.tools = tools # SOCtools instance
    async def evaluar(
        self, 
        decision: Decision, 
        contexto: ContextoEscenario,
        contexto_rag: str = "",
        memoria_episodica: str = ""
    ) -> EvaluacionTecnica:
        """Executes technical evaluation using ReAct in English."""
        
        # 1. Use provided RAG context or retrieve if missing
        if not contexto_rag:
            print(f"  [Analyst] No context provided. Retrieving via RAG...")
            rag_result = self.rag.retrieve_with_context(
                decision=decision.model_dump(),
                contexto=contexto.model_dump(),
                k=3
            )
            contexto_rag = rag_result["contexto_rag"]
        
        # 2. Prepare ReAct
        if not self.tools:
            return await self._simple_eval(decision, contexto, contexto_rag)

        tools_list = self.tools.get_tools()
        tools_desc = "\n".join([f"- {t.name}: {t.description}" for t in tools_list])
        
        prompt = REACT_PROMPT_ANALISTA.format(
            tools_desc=tools_desc,
            accion=decision.accion,
            target=decision.target,
            tipo_incidente=contexto.tipo_incidente,
            fase=contexto.fase,
            contexto_rag=contexto_rag,
            memoria_episodica=memoria_episodica if memoria_episodica else "No previous history in this session."
        )
        
        import hashlib
        
        # 3. Phase 1: Strategic Thinking (Tool-free deliberation)
        # We ask the LLM to create a plan before using tools
        planning_prompt = f"Technical context: {contexto_rag}\nUser Action: {decision.accion} on {decision.target}\n\nTask: Develop a technical investigation plan (2 sentences) before using any tools."
        strategy = await self.llm.generate(planning_prompt)
        print(f"  [Analyst] Strategic Thinking: {strategy}")
        
        # 4. Phase 2: Reasoning Loop (ReAct)
        reasoning_chain = [f"Initial Plan: {strategy}"]
        mcp_results = []
        action_history_hashes = set()
        max_iterations = 3 # Increased slightly to allow more depth
        current_prompt = prompt + f"\nInitial Strategy: {strategy}"
        
        print(f"  [Analyst] Starting reasoning chain (ReAct in English)...")
        
        for i in range(max_iterations):
            response = await self.llm.generate(current_prompt)
            reasoning_chain.append(response)
            
            # Search for Action in English
            action_match = re.search(r"Action: (\w+)", response)
            action_input_match = re.search(r"Action Input: (.*)", response)
            
            if action_match and action_input_match:
                action_name = action_match.group(1).strip()
                action_input = action_input_match.group(1).strip()
                
                # LOOP DETECTION (Phase 3 of Manual)
                call_id = hashlib.md5(f"{action_name}:{action_input}".encode()).hexdigest()
                if call_id in action_history_hashes:
                    print(f"    → [Circuit Breaker] Loop detected: {action_name} with same input. Breaking.")
                    current_prompt += f"\nObservation: [SYSTEM] Tool loop detected. You already tried this exact action. Please change your strategy or provide a Final Answer."
                    continue
                
                action_history_hashes.add(call_id)
                print(f"    → Action {i+1}: {action_name}('{action_input}')")
                
                # Execute tool
                obs = "Tool not found"
                for t in tools_list:
                    if t.name == action_name:
                        # Si el input parece un JSON, lo parseamos a dict
                        input_to_pass = action_input
                        if action_input.startswith("{") and action_input.endswith("}"):
                            try:
                                input_to_pass = json.loads(action_input)
                            except:
                                pass
                                
                        # Usar ainvoke para herramientas asíncronas
                        obs = await t.ainvoke(input_to_pass)
                        # Si la observación es un JSON, intentamos guardarla como dato técnico
                        try:
                            # Si obs no es string, lo convertimos para el log
                            obs_str = str(obs) if not isinstance(obs, str) else obs
                            parsed_obs = json.loads(obs_str)
                            if isinstance(parsed_obs, list):
                                mcp_results.extend(parsed_obs)
                            else:
                                mcp_results.append(parsed_obs)
                        except:
                            pass
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
            result_json = await self.llm.generate_json(f"Based on this technical reasoning, generate the evaluation JSON: {reasoning_chain[-1]}")
        
        tracer.add_step("Analyst_Reasoning_Chain", {"chain": reasoning_chain})

        # Extraer hashes REALES del contexto RAG
        real_hashes = re.findall(r"Hash: ([a-f0-9]+)", contexto_rag)

        # Sanitize outputs
        def ensure_string(val: Any) -> str:
            if isinstance(val, (dict, list)):
                return str(val)
            return str(val) if val is not None else ""
        # Sanitize artifacts to avoid Pydantic validation errors from LLM noise
        raw_artifacts = result_json.get("verified_artifacts", [])
        clean_artifacts = []
        if isinstance(raw_artifacts, list):
            for art in raw_artifacts:
                if isinstance(art, dict) and "fact" in art:
                    # Ensure all required fields exist with defaults if missing
                    clean_artifacts.append({
                        "fact": ensure_string(art.get("fact", "Dato técnico")),
                        "certainty": int(art.get("certainty", 100)) if str(art.get("certainty", "")).isdigit() else 100,
                        "source": art.get("source", "inference") if art.get("source") in ["tool", "rag", "inference"] else "inference"
                    })

        try:
            return EvaluacionTecnica(
                analysis=ensure_string(result_json.get("analysis", "Technical analysis completed")),
                explanation=ensure_string(result_json.get("explanation", "No detailed explanation provided")),
                strengths=result_json.get("strengths", []),
                weaknesses=result_json.get("weaknesses", []),
                best_practice=ensure_string(result_json.get("best_practice", "Consult standard manuals")),
                sources=result_json.get("sources", []),
                technical_score=int(result_json.get("technical_score", 70)) if str(result_json.get("technical_score", "")).isdigit() else 70,
                resilience_score=int(result_json.get("resilience_score", 70)) if str(result_json.get("resilience_score", "")).isdigit() else 70,
                forensic_notes=ensure_string(result_json.get("forensic_notes")),
                source_integrity_hashes=real_hashes,
                technical_data=mcp_results,
                verified_artifacts=clean_artifacts
            )
        except Exception as e:
            print(f" [AnalystAgent] Error creating EvaluacionTecnica: {e}")
            print(f" [AnalystAgent] JSON was: {result_json}")
            # Fallback
            return EvaluacionTecnica(
                analysis="Error processing evaluation.",
                explanation=f"Internal error: {str(e)}",
                strengths=[], weaknesses=[],
                best_practice="Check system logs.",
                sources=[], technical_score=0, resilience_score=0,
                verified_artifacts=[]
            )




    async def _simple_eval(self, decision: Decision, contexto: ContextoEscenario, contexto_rag: str, memoria_episodica: str = "") -> EvaluacionTecnica:
        """Simple fallback without tools, using English prompts."""
        contexto_dict = contexto.model_dump()
        contexto_dict['memoria_episodica'] = memoria_episodica
        prompt = build_prompt_analista(
            decision=decision.model_dump(),
            contexto=contexto_dict,
            contexto_rag=contexto_rag
        )
        result = await self.llm.generate_json(prompt)
        
        # Sanitize artifacts to avoid Pydantic validation errors from LLM noise
        raw_artifacts = result.get("verified_artifacts", [])
        clean_artifacts = []
        if isinstance(raw_artifacts, list):
            for art in raw_artifacts:
                if isinstance(art, dict) and "fact" in art:
                    clean_artifacts.append({
                        "fact": str(art.get("fact", "Dato técnico")),
                        "certainty": int(art.get("certainty", 100)) if str(art.get("certainty", "")).isdigit() else 100,
                        "source": art.get("source", "inference") if art.get("source") in ["tool", "rag", "inference"] else "inference"
                    })

        return EvaluacionTecnica(
            analysis=result.get("analysis", "Direct analysis"),
            explanation=result.get("explanation", "Standard fallback explanation"),
            strengths=result.get("strengths", []),
            weaknesses=result.get("weaknesses", []),
            best_practice=result.get("best_practice", "Consult NIST 800-61"),
            sources=result.get("sources", []),
            technical_score=int(result.get("technical_score", 50)) if str(result.get("technical_score", "")).isdigit() else 50,
            resilience_score=int(result.get("resilience_score", 50)) if str(result.get("resilience_score", "")).isdigit() else 50,
            forensic_notes=result.get("forensic_notes"),
            source_integrity_hashes=real_hashes,
            verified_artifacts=clean_artifacts
        )