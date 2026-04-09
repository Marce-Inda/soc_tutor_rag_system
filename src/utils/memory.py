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
                "last_updated": datetime.now().isoformat()
            }
            
        with open(path, 'r') as f:
            try:
                # Si existe exitosamente devolvemos el diario completo traducido a código de lectura inmediata.
                return json.load(f)
            except BaseException:
                # Medida defensiva: Si el archivo se corrompió de casualidad; proveemos una copia de relleno vacía por defecto
                return {
                    "session_id": session_id,
                    "created_at": datetime.now().isoformat(),
                    "steps": [],
                    "last_updated": datetime.now().isoformat()
                }
            
    def get_history_summary(self, session_id: str) -> str:
        """
        Herramienta clave (Táctico): Hace un 'Resumen Ejecutivo'.
        Convierte esa libreta posiblemente larga y detallada en un párrafo super compacto (Toma 1, 2, 3...) 
        para poder insertarlo limpio en el contexto de un nuevo chat de la IA. Si enviáramos el 
        archivo json completo sin limpiarlo, podríamos saturar o confundir al modelo lingüístico.
        """
        data = self.load_session(session_id)
        steps = data.get("steps", [])
        
        if not steps:
            return "El jugador recién acaba de conectarse. Todavía carece de antecedentes de decisiones tomadas."
            
        summary = "HISTORIAL RESUMIDO DE LAS DECISIONES PREVIAS DEL JUGADOR:\n"
        for i, step in enumerate(steps):
            accion = step.get("decision", {}).get("accion", "N/A")
            target = step.get("decision", {}).get("target", "N/A")
            summary += f"[{i+1}] Acción ejecutada: '{accion}' -> aplicada directamente hacia: '{target}' \n"
            
        return summary
