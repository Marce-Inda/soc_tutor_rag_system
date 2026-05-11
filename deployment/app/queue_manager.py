import time
import random
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel

class QueueStatus(BaseModel):
    status: str  # "ACTIVE", "WAITING", "EXPIRED"
    position: int
    codename: str
    is_ready: bool

class QueueManager:
    """
    Gestiona la concurrencia de usuarios y la lista de espera.
    Implementa un sistema de nombres clave estilo anime.
    """
    
    def __init__(self, max_concurrent: int = 2, heartbeat_timeout: int = 45):
        self.max_concurrent = max_concurrent
        self.heartbeat_timeout = heartbeat_timeout
        
        # user_id -> last_heartbeat
        self.active_users: Dict[str, float] = {}
        # List of user_ids in waiting queue
        self.waiting_queue: List[str] = []
        # user_id -> last_heartbeat
        self.waiting_heartbeats: Dict[str, float] = {}
        # user_id -> session_start_time
        self.session_starts: Dict[str, float] = {}
        # user_id -> codename
        self.codenames: Dict[str, str] = {}
        
        self.max_session_duration = 30 * 60  # 30 minutos máximo por sesión
        
        self.anime_prefixes = [
            "Neo", "Ghost", "Zero", "Alpha", "Shadow", "Cloud", "Void", 
            "Nova", "Cyber", "Mecha", "Shin", "Psycho", "Iron", "Dark"
        ]
        self.anime_suffixes = [
            "Vortex", "Shell", "One", "Prime", "Shinji", "Kusanagi", "Striker",
            "Babel", "Pulse", "Hunter", "Drive", "System", "Protocol", "Edge"
        ]

    def _generate_codename(self, user_id: str) -> str:
        if user_id not in self.codenames:
            p = random.choice(self.anime_prefixes)
            s = random.choice(self.anime_suffixes)
            num = random.randint(10, 99)
            self.codenames[user_id] = f"{p}-{s}-{num}".upper()
        return self.codenames[user_id]

    def _cleanup_stale_users(self):
        """Elimina usuarios que no han enviado heartbeat."""
        now = time.time()
        
        # Limpiar usuarios activos (por inactividad O por tiempo máximo excedido)
        stale_active = [uid for uid, last in self.active_users.items() if now - last > self.heartbeat_timeout]
        expired_sessions = [uid for uid, start in self.session_starts.items() if uid in self.active_users and now - start > self.max_session_duration]
        
        for uid in set(stale_active + expired_sessions):
            print(f"[Queue] Usuario expulsado (inactivo/expirado): {uid}")
            if uid in self.active_users:
                del self.active_users[uid]
            if uid in self.session_starts:
                del self.session_starts[uid]
            if uid in self.codenames:
                del self.codenames[uid]
            
        # Limpiar cola de espera
        stale_waiting = [uid for uid, last in self.waiting_heartbeats.items() if now - last > self.heartbeat_timeout]
        for uid in stale_waiting:
            print(f"[Queue] Usuario en espera expirado: {uid}")
            if uid in self.waiting_queue:
                self.waiting_queue.remove(uid)
            if uid in self.waiting_heartbeats:
                del self.waiting_heartbeats[uid]
            if uid in self.codenames:
                del self.codenames[uid]

        # Promocionar usuarios de la cola a activos si hay espacio
        while len(self.active_users) < self.max_concurrent and self.waiting_queue:
            next_user = self.waiting_queue.pop(0)
            if next_user in self.waiting_heartbeats:
                del self.waiting_heartbeats[next_user]
            self.active_users[next_user] = now
            self.session_starts[next_user] = now
            print(f"[Queue] Usuario promocionado a ACTIVO: {next_user}")

    def get_user_status(self, user_id: str) -> QueueStatus:
        self._cleanup_stale_users()
        now = time.time()
        codename = self._generate_codename(user_id)

        # 1. Ya es activo
        if user_id in self.active_users:
            self.active_users[user_id] = now
            return QueueStatus(status="ACTIVE", position=0, codename=codename, is_ready=True)

        # 2. Hay espacio y no estaba activo
        if len(self.active_users) < self.max_concurrent and user_id not in self.waiting_queue:
            self.active_users[user_id] = now
            if user_id not in self.session_starts:
                self.session_starts[user_id] = now
            return QueueStatus(status="ACTIVE", position=0, codename=codename, is_ready=True)

        # 3. Debe ir a la cola o ya está en ella
        if user_id not in self.waiting_queue:
            self.waiting_queue.append(user_id)
        
        self.waiting_heartbeats[user_id] = now
        pos = self.waiting_queue.index(user_id) + 1
        
        return QueueStatus(status="WAITING", position=pos, codename=codename, is_ready=False)

    def heartbeat(self, user_id: str):
        """Actualiza el tiempo de actividad del usuario."""
        now = time.time()
        if user_id in self.active_users:
            self.active_users[user_id] = now
        elif user_id in self.waiting_heartbeats:
            self.waiting_heartbeats[user_id] = now
        else:
            # Re-evaluar si se perdió el tracking
            return self.get_user_status(user_id)
        return None

    def expel_user(self, user_id: str):
        """Expulsa forzosamente a un usuario del sistema (ej. por agotar turnos o costo)."""
        if user_id in self.active_users:
            del self.active_users[user_id]
        if user_id in self.session_starts:
            del self.session_starts[user_id]
        if user_id in self.waiting_queue:
            self.waiting_queue.remove(user_id)
        if user_id in self.waiting_heartbeats:
            del self.waiting_heartbeats[user_id]
        if user_id in self.codenames:
            del self.codenames[user_id]
        print(f"[Queue] Usuario expulsado forzosamente: {user_id}")
