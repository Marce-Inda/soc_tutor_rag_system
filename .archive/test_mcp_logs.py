import asyncio
from src.agents.tools import SOCtools

class MockRAG:
    pass

tools = SOCtools(MockRAG())

print("=== Testing Get ALL Logs ===")
print(tools.consultar_telemetria_mcp(action_type="analyze_logs")[0:200] + "...")

print("\n=== Testing Evaluate SPECIFIC Log ===")
print(tools.consultar_telemetria_mcp(action_type="evaluate_selected_log", target="L-003"))
