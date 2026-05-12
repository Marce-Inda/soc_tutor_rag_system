"""
Sistema de Memoria a Corto Plazo (Persistente) para el sistema del Tutor.
Al igual que un humano, si la Inteligencia Artificial no guarda apuntes, 
olvidará todo en cuanto le hagamos una nueva pregunta.
Este archivo construye un "diario de vida" o "bitácora" en donde va anotando 
cada paso, decisión y acción del jugador durante la sesión actual (o partida de juego).
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class SessionMemory:
    """Manejador o 'Bibliotecario' silencioso de la sesión actual del jugador."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """Prepara el directorio secreto (la carpeta) en donde guardaremos físicamente todas las libretas de apuntes."""
        if not storage_dir:
            base_dir = Path(__file__).parent.parent.parent
            storage_dir = str(base_dir / "data" / "sessions")
        
        self.storage_dir = storage_dir
        # Aseguramos que la carpeta digital exista en la computadora. Si no existe aún, ¡la crea sola!
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def _get_path(self, session_id: str) -> Path:
        """Crea la dirección o ruta exacta del archivo puntual (ej. minombresesion.json)."""
        return Path(self.storage_dir) / f"{session_id}.json"
    
    def save_step(self, session_id: str, step_data: Dict[str, Any]):
        """
        Guarda un nuevo acontecimiento vital en la bitácora del jugador 
        (ej. 'El jugador decidió bloquear la Mac-Address atacante a las 14:00 hrs').
        """
        path = self._get_path(session_id)
        
        # Primero abrimos el viejo diario para empaparnos de qué más había antes
        data = self.load_session(session_id)
        
        # Agregamos la fecha y hora precisa a esta acción reciente, como si fuera un sello policial oficial de su movimiento
        if "timestamp" not in step_data:
            step_data["timestamp"] = datetime.now().isoformat()
            
        # Anexamos (append) este nuevo paso a la gran lista y actualizamos el récord general de modificación
        data["steps"].append(step_data)
        data["last_updated"] = datetime.now().isoformat()
        
        # Guardamos todo de vuelta en el disco duro físico para no perder datos ni por un apagón
        with open(path, 'w') as f:
            json.dump(data, f, default=str, indent=2)

    def save_pending_evaluation(self, session_id: str, analista_data: Dict, gobernanza_data: Dict):
        """Saves evaluation data for an action that was paused for HITL."""
        path = self._get_path(session_id)
        data = self.load_session(session_id)
        data["pending_hitl"] = {
            "analista": analista_data,
            "gobernanza": gobernanza_data,
            "timestamp": datetime.now().isoformat()
        }
        with open(path, 'w') as f:
            json.dump(data, f, default=str, indent=2)

    def load_pending_evaluation(self, session_id: str) -> Optional[Dict]:
        """Loads and clears pending HITL data."""
        path = self._get_path(session_id)
        data = self.load_session(session_id)
        pending = data.get("pending_hitl")
        if pending:
            # Clear it after loading to avoid re-processing the same confirm
            del data["pending_hitl"]
            with open(path, 'w') as f:
                json.dump(data, f, default=str, indent=2)
        return pending
            
    def load_session(self, session_id: str) -> Dict[str, Any]:
        """
        Abre y saca todas las memorias pasadas de una misma sesión para que la IA refresque su razonamiento interno.
        """
        path = self._get_path(session_id)
        
        # Si es la primera vez que interactuamos (nueva partida) y no existe un viejo diario, crea uno fresco y sin anotaciones.
        if not path.exists():
            return {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "steps": [], # Vacío
                "artifact_index": [],
                "history_summary": "", # New: Summary of old turns
                "last_updated": datetime.now().isoformat()
            }
            
        with open(path, 'r') as f:
            try:
                # Si existe exitosamente devolvemos el diario completo traducido a código de lectura inmediata.
                data = json.load(f)
                if "artifact_index" not in data:
                    data["artifact_index"] = []
                if "history_summary" not in data:
                    data["history_summary"] = ""
                return data
            except BaseException:
                # Medida defensiva: Si el archivo se corrompió de casualidad; proveemos una copia de relleno vacía por defecto
                return {
                    "session_id": session_id,
                    "created_at": datetime.now().isoformat(),
                    "steps": [],
                    "artifact_index": [],
                    "history_summary": "",
                    "last_updated": datetime.now().isoformat()
                }
            
    def get_audit_trail(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Returns only the snapshots and technical actions for auditing.
        This enables 'Why did the agent take this decision?' forensics.
        """
        data = self.load_session(session_id)
        return [step for step in data.get("steps", []) if "snapshot" in step or step.get("action") == "JUSTIFICATION"]

    def update_artifact_index(self, session_id: str, new_artifacts: List[Any]):
        """Agrega nuevos hallazgos confirmados al índice de artefactos de la sesión."""
        path = self._get_path(session_id)
        data = self.load_session(session_id)
        
        current_artifacts = data.get("artifact_index", [])
        # Usamos el campo 'fact' como identificador único para evitar duplicados
        existing_facts = set()
        for a in current_artifacts:
            if isinstance(a, dict):
                existing_facts.add(a.get("fact"))
            else:
                existing_facts.add(a)
        
        for art in new_artifacts:
            fact = art.get("fact") if isinstance(art, dict) else art
            if fact not in existing_facts:
                current_artifacts.append(art)
                existing_facts.add(fact)
        
        data["artifact_index"] = current_artifacts
        data["last_updated"] = datetime.now().isoformat()

        
        with open(path, 'w') as f:
            json.dump(data, f, default=str, indent=2)

    def update_history_summary(self, session_id: str, summary: str):
        """Actualiza el resumen consolidado de la sesión."""
        path = self._get_path(session_id)
        data = self.load_session(session_id)
        
        data["history_summary"] = summary
        data["last_updated"] = datetime.now().isoformat()
        
        with open(path, 'w') as f:
            json.dump(data, f, default=str, indent=2)

    def get_last_step_timestamp(self, session_id: str) -> Optional[float]:
        """Retorna el timestamp de la última acción guardada en segundos."""
        data = self.load_session(session_id)
        steps = data.get("steps", [])
        if not steps:
            return None
        
        last_ts_str = steps[-1].get("timestamp")
        if not last_ts_str:
            return None
            
        try:
            dt = datetime.fromisoformat(last_ts_str)
            return dt.timestamp()
        except:
            return None

    def get_artifact_summary(self, session_id: str) -> str:
        """Retorna un resumen de los artefactos/evidencias confirmadas hasta ahora."""
        data = self.load_session(session_id)
        artifacts = data.get("artifact_index", [])
        if not artifacts:
            return "No se han consolidado evidencias técnicas oficiales aún."
            
        summary = "GROUND TRUTH / ARTIFACT INDEX (Verified Findings):\n"
        for art in artifacts:
            # Handle both old string format and new dict format for backward compatibility
            if isinstance(art, dict):
                fact = art.get("fact", "N/A")
                cert = art.get("certainty", 100)
                src = art.get("source", "tool").upper()
                summary += f"- [{cert}% {src}] {fact}\n"
            else:
                summary += f"- [100% CONFIRMED] {art}\n"
        return summary

    def get_history_summary(self, session_id: str) -> str:
        """
        Herramienta clave (Táctico): Hace un 'Resumen Ejecutivo'.
        Convierte esa libreta posiblemente larga y detallada en un párrafo super compacto.
        Incluye el Artifact Index para mayor grounding y el history_summary si existe.
        """
        data = self.load_session(session_id)
        steps = data.get("steps", [])
        history_summary = data.get("history_summary", "")
        
        artifact_sum = self.get_artifact_summary(session_id)
        
        if not steps and not history_summary:
            return f"{artifact_sum}\n\nEl jugador recién acaba de conectarse. Todavía carece de antecedentes de decisiones tomadas."
            
        summary = f"{artifact_sum}\n\n"
        
        if history_summary:
            summary += f"RESUMEN CONSOLIDADO DE TURNOS ANTERIORES:\n{history_summary}\n\n"
            summary += "DECISIONES RECIENTES:\n"
        else:
            summary += "HISTORIAL DE LAS DECISIONES DEL JUGADOR:\n"

        for i, step in enumerate(steps):
            accion = step.get("decision", {}).get("accion", "N/A")
            target = step.get("decision", {}).get("target", "N/A")
            summary += f"[{i+1}] Acción ejecutada: '{accion}' -> aplicada hacia: '{target}' \n"
            
        return summary

    def get_session_turn_count(self, session_id: str) -> int:
        """
        Devuelve el número de turnos (decisiones) guardados en esta sesión.
        """
        data = self.load_session(session_id)
        return len(data.get("steps", []))

    def get_history_token_count(self, session_id: str) -> int:
        """
        Calcula una estimación del conteo de tokens de la historia completa.
        Utiliza el TokenCounter oficial del sistema.
        """
        from .token_counter import TokenCounter
        history = self.get_history_summary(session_id)
        return TokenCounter.count_tokens(history)


