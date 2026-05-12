import asyncio
from src.agents.types import Decision, ContextoEscenario
from src.agents.analyst_agent import AnalystAgent
import traceback

class DummyLLM:
    async def generate(self, prompt, sys_prompt=None):
        return """
        {
          "analysis": "...",
          "verified_artifacts": [
            "fact": "technical fact"
          ]
        }
        """
    async def generate_json(self, prompt, sys_prompt=None):
        raise ValueError('Falla crítica, no se pudo entender la respuesta JSON de la IA: {"fact": ""}')
    def get_provider(self): return "dummy"
    @property
    def last_usage(self): return {}

class DummyRAG:
    def retrieve_with_context(self, *args, **kwargs):
        return {"contexto_rag": "dummy"}

async def main():
    agent = AnalystAgent(DummyLLM(), DummyRAG())
    dec = Decision(accion="test", target="test")
    ctx = ContextoEscenario(tipo_incidente="test", fase="test")
    try:
        res = await agent.evaluar(dec, ctx)
        print("Success!", res)
    except Exception as e:
        print(f"Error Type: {type(e)}")
        print(f"Error repr: {repr(e)}")
        print(f"Error str: {str(e)}")

asyncio.run(main())
