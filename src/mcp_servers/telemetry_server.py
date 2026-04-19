import json
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Inicializar FastMCP Server
mcp = FastMCP("telemetry_server")

def get_logs_data():
    """Helper function to load the local synthetic dataset."""
    file_path = Path("data/sample_scenarios/es-tourism-gdpr-email-breach/evidence/siem_dump.json")
    if not file_path.exists():
        # Fallback si se corre desde otro lado o no está el archivo
        return [{"log_id": "L-ERR", "message": "Log file not found at " + str(file_path)}]
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Recurso MCP para la herramienta interactiva de frontend 
@mcp.resource("siem://incident-001/smtp-logs")
def get_smtp_logs() -> str:
    """Gets the entire raw SIEM log dataset for the current GDPR incident as a JSON string for the UI."""
    data = get_logs_data()
    return json.dumps(data, indent=2)

# Nueva Herramienta MCP para que el IA evalúe un log específico elegido por el jugador
@mcp.tool()
def get_specific_log(log_id: str) -> str:
    """Retrieves a specific log entry by its log_id. Useful when the user selects a specific log to evaluate."""
    data = get_logs_data()
    for log in data:
        if log.get("log_id") == log_id:
            return json.dumps(log, indent=2)
    return f"Log with ID {log_id} not found."

# Herramienta MCP para "NetScan"
@mcp.tool()
def execute_ndr_scan(target_ip: str) -> str:
    """Executes a simulated Network Detection and Response (NDR) scan on a target IP or hostname. Use this to verify active connections in an incident."""
    if target_ip in ["SRV-SWIFT-01", "SMTP-Relay-Main", "localhost"]:
         return '{"active_connections": [{"remote_ip": "1.2.3.4", "state": "ESTABLISHED", "risk": "High", "process": "powershell.exe"}, {"remote_ip": "10.0.0.5", "state": "LISTEN", "risk": "Low", "process": "sshd"}]}'
    return '{"active_connections": []}'

if __name__ == "__main__":
    mcp.run()
