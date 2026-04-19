import asyncio
from src.agents.tools import SOCtools

class MockRAG:
    pass

tools = SOCtools(MockRAG())

print("=== Testing Isolate Host via MCP ===")
res_isolate = tools.ejecutar_accion_edr_mcp(action_type="isolate_host", target="SRV-SWIFT-01")
print(res_isolate)

print("\n=== Testing Block IP via MCP ===")
res_block = tools.ejecutar_accion_edr_mcp(action_type="block_ip", target="172.16.0.40")
print(res_block)
