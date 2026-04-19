import asyncio
from src.agents.tools import SOCtools

class MockRAG:
    pass

# Initialize tools
tools = SOCtools(MockRAG())

# Test SIEM Logs
print("=== Testing SIEM Logs via MCP ===")
result_logs = tools.consultar_telemetria_mcp(action_type="analyze_logs")
print(result_logs)

# Test NDR Scan
print("\n=== Testing NDR Scan via MCP ===")
result_scan = tools.consultar_telemetria_mcp(action_type="network_scan", target="localhost")
print(result_scan)
