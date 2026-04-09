"""
Módulo de Observabilidad (Cronómetro y Caja Negra Técnica) para todo tu entorno de seguridad.
Este código existe para cuidarnos las espaldas a largo plazo: hace una audición invisible midiendo 
cuánto demora o le cuesta a nuestra IA responderle a un usuario (esta es su Latencia de tiempo e
impacta directamente en el ritmo o feeling del juego).
También deja grabados todos y cada uno de los trazos técnicos exactos por si fallamos, tener siempre a la mano
la 'caja negra de avión' lista para depurarse si un evaluador descubre problemas de código.
"""

import time
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class UEFS_Tracer:
    """Herramienta o clase que implementa de forma sencilla y eficiente el Rastreador (Caja negra)."""
    
    def __init__(self, log_dir: str = "logs/traces"):
        """Establece inicialmente la guarida o directorio oculto en el servidor donde guardaremos estas copias o logs."""
        base_dir = Path(__file__).parent.parent.parent
        self.log_dir = base_dir / log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.current_trace = {}

    def start_trace(self, operation: str, metadata: Dict[str, Any]):
        """
        Pistolazo inicial: Enciende el cronómetro o reloj biológico, e indica exactamente 
        qué tipo de acción estamos emprendiendo ahora, cuándo se inició temporalmente este turno 
        y con qué cuentas y datos de juego estamos respaldándolo todo en el ecosistema (esto último es Metadata).
        """
        self.current_trace = {
            "operation": operation,
            "start_time": datetime.now().isoformat(),
            "metadata": metadata, # Anotaciones accesorias (Ej: "Misión Actual es Nivel Experto, y Jugador123 la inició")
            "steps": [],
            "status": "in_progress" # Lo colgamos provisionalmente en curso o progreso
        }
        # Activamos el motor subyacente que arranca a contabilizar cada tick y tock desde ahora.
        self._start_perf = time.perf_counter()

    def add_step(self, step_name: str, details: Dict[str, Any]):
        """
        Agrega pausas comerciales o hitos intermedios. Marca pasos logrados internamente.
        Muy útil para chequear con detalle si el evento global falló, por ejemplo en el hito 2 o el 4.
        """
        self.current_trace["steps"].append({
            "name": step_name,
            "timestamp": datetime.now().isoformat(),
            "details": details
        })

    def end_trace(self, result: Dict[str, Any], status: str = "success"):
        """
        Este apagador frena de súbito el reloj interno iniciado antes, evalúa la resta temporal exacta de todos los sucesos, 
        y por último empaqueta la colección maestra como un reporte histórico, volcándolo estáticamente al sistema de archivos físicos dentro del equipo.
        """
        duration = time.perf_counter() - self._start_perf
        self.current_trace.update({
            "end_time": datetime.now().isoformat(),
            "duration_sec": round(duration, 4), # Calcula con extremada certeza (hasta los 4 dígitos remanentes decimales) el gasto productivo medido estrictamente en Segundos.
            "status": status,
            "result_summary": {k: type(v).__name__ for k, v in result.items()}
        })
        
        # Personalizamos dinámicamente un nombre distinto para cada factura de reporte técnico apelando a las variables temporales presentes para no tapar los viejos.
        filename = f"reporte_tecnico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Empuja esta escritura sólida bajo un formato indexado a JSON adentro de la carpeta definida en la inicialización
        with open(self.log_dir / filename, 'w') as f:
            json.dump(self.current_trace, f, indent=2)
            
        return self.current_trace

# Variable Global Compartida (Arquitectura "Singleton"): 
# Levantamos y encendemos solo y estricamente 1 mismo y exacto reloj central o master tracer y lo exportaremos 
# libremente por el juego para forzar a que todo mundo comparta las variables del trazador principal.
tracer = UEFS_Tracer()
