import json
import os
import sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Inicializar FastMCP Server
mcp = FastMCP("telemetry_server")

# Configuración: Permitir inyectar el banco de evidencias desde el exterior
DEFAULT_BANK = "data/sample_scenarios/evidence_bank_001.json"
SCENARIO_BANK_PATH = os.getenv("SCENARIO_BANK_PATH", DEFAULT_BANK)

def get_evidence_bank():
    """Helper function to load the centralized evidence bank."""
    file_path = Path(SCENARIO_BANK_PATH)
    
    if not file_path.exists():
        # Fallback al default si el inyectado no existe
        file_path = Path(DEFAULT_BANK)
        if not file_path.exists():
            return {"scenario_id": "error", "evidence": [], "error": f"Bank not found at {SCENARIO_BANK_PATH} or {DEFAULT_BANK}"}
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"scenario_id": "error", "evidence": [], "error": str(e)}

@mcp.resource("siem://current-scenario/logs")
def get_siem_logs() -> str:
    """Gets all logs available for the Log Analyzer tool in the current active scenario."""
    bank = get_evidence_bank()
    if "error" in bank:
        return json.dumps(bank, indent=2)
        
    logs = [e for e in bank["evidence"] if e["tool"] == "LOG_ANALYZER"]
    return json.dumps(logs, indent=2)

@mcp.tool()
def get_specific_evidence(evidence_id: str) -> str:
    """Retrieves a specific evidence entry by its ID from the current scenario."""
    bank = get_evidence_bank()
    if "error" in bank:
        return json.dumps(bank, indent=2)
        
    for entry in bank["evidence"]:
        if entry["id"] == evidence_id:
            return json.dumps(entry, indent=2)
    return f"Evidence with ID {evidence_id} not found in scenario {bank.get('scenario_id')}."

@mcp.tool()
def execute_ndr_scan(target_ip: str) -> str:
    """Executes a simulated Network Detection and Response (NDR) scan. Returns data from the active scenario's bank."""
    bank = get_evidence_bank()
    if "error" in bank:
        return json.dumps(bank, indent=2)
        
    scan_data = [e for e in bank["evidence"] if e["tool"] == "NETSCAN"]
    # En el futuro, podríamos filtrar por target_ip si el banco lo soporta
    if scan_data:
        return json.dumps(scan_data[0], indent=2)
    return '{"active_connections": [], "status": "no_threats_detected"}'

@mcp.resource("scenario://active/metadata")
def get_scenario_metadata() -> str:
    """Returns metadata about the currently active scenario."""
    bank = get_evidence_bank()
    metadata = {
        "scenario_id": bank.get("scenario_id"),
        "evidence_count": len(bank.get("evidence", [])),
        "disclaimer": bank.get("disclaimer")
    }
    return json.dumps(metadata, indent=2)

if __name__ == "__main__":
    mcp.run()
