"""
Módulo de Observabilidad para el sistema UEFS.
Rastreo de latencia, uso de tokens y costos estimados.
"""

import time
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class UEFS_Tracer:
    """Implementación simple para observabilidad."""
    
    def __init__(self, log_dir: str = "logs/traces"):
        base_dir = Path(__file__).parent.parent.parent
        self.log_dir = base_dir / log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.current_trace = {}

    def start_trace(self, operation: str, metadata: Dict[str, Any]):
        """Inicia el rastreo de una operación."""
        self.current_trace = {
            "operation": operation,
            "start_time": datetime.now().isoformat(),
            "metadata": metadata,
            "steps": [],
            "status": "in_progress"
        }
        self._start_perf = time.perf_counter()

    def add_step(self, step_name: str, details: Dict[str, Any]):
        """Agrega un paso intermedio al rastro."""
        self.current_trace["steps"].append({
            "name": step_name,
            "timestamp": datetime.now().isoformat(),
            "details": details
        })

    def end_trace(self, result: Dict[str, Any], status: str = "success"):
        """Finaliza y guarda el rastro."""
        duration = time.perf_counter() - self._start_perf
        self.current_trace.update({
            "end_time": datetime.now().isoformat(),
            "duration_sec": round(duration, 4),
            "status": status,
            "result_summary": {k: type(v).__name__ for k, v in result.items()}
        })
        
        # Guardar en archivo
        filename = f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(self.log_dir / filename, 'w') as f:
            json.dump(self.current_trace, f, indent=2)
            
        return self.current_trace

tracer = UEFS_Tracer()
