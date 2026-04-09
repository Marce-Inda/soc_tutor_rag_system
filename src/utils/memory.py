"""
Sistema de memoria persistente para el sistema UEFS.
Permite realizar seguimiento de las decisiones del jugador en una sesión.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class SessionMemory:
    """Maneja la persistencia de la sesión del jugador."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        if not storage_dir:
            base_dir = Path(__file__).parent.parent.parent
            storage_dir = str(base_dir / "data" / "sessions")
        
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def _get_path(self, session_id: str) -> Path:
        return Path(self.storage_dir) / f"{session_id}.json"
    
    def save_step(self, session_id: str, step_data: Dict[str, Any]):
        """Guarda un paso de la sesión."""
        path = self._get_path(session_id)
        
        data = self.load_session(session_id)
        
        # Agregar timestamp si no existe
        if "timestamp" not in step_data:
            step_data["timestamp"] = datetime.now().isoformat()
            
        data["steps"].append(step_data)
        data["last_updated"] = datetime.now().isoformat()
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
            
    def load_session(self, session_id: str) -> Dict[str, Any]:
        """Carga la historia de una sesión."""
        path = self._get_path(session_id)
        
        if not path.exists():
            return {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "steps": [],
                "last_updated": datetime.now().isoformat()
            }
            
        with open(path, 'r') as f:
            return json.load(f)
            
    def get_history_summary(self, session_id: str) -> str:
        """Retorna un resumen de la historia para el contexto del LLM."""
        data = self.load_session(session_id)
        steps = data.get("steps", [])
        
        if not steps:
            return "No hay historial previo en esta sesión."
            
        summary = "HISTORIAL DE DECISIONES PREVIAS:\n"
        for i, step in enumerate(steps):
            accion = step.get("decision", {}).get("accion", "N/A")
            target = step.get("decision", {}).get("target", "N/A")
            summary += f"{i+1}. Acción: {accion} sobre {target}\n"
            
        return summary
