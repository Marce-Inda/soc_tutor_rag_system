import hashlib
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Set

class UniversalAgentHarness:
    """
    UAH: Universal Agent Harness Boilerplate.
    A production-grade control layer for autonomous agents.
    
    Features:
    - Loop Detection (MD5)
    - Artifact Indexing (Ground Truth)
    - Strategic Deliberation (Think-before-Act)
    - Context Monitoring (Turn Tracking)
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.action_history_hashes: Set[str] = set()
        self.artifact_index: Set[str] = set()
        self.turn_count = 0
        self.start_time = datetime.now()

    # --- PYLAR 1: LOOP DETECTION ---
    def check_loop(self, tool_name: str, arguments: Any) -> bool:
        """
        Hashes tool calls to detect redundancy.
        Returns True if a loop is detected.
        """
        call_str = f"{tool_name}:{str(arguments)}"
        call_hash = hashlib.md5(call_str.encode()).hexdigest()
        
        if call_hash in self.action_history_hashes:
            return True
        
        self.action_history_hashes.add(call_hash)
        return False

    # --- PILAR 2: ARTIFACT INDEXING ---
    def extract_and_index(self, text: str, pattern: str = r"EV_[A-Z0-9_]+"):
        """
        Scans agent output for specific identifiers and adds them to the index.
        Default pattern targets 'EV_...' style evidence IDs.
        """
        found = re.findall(pattern, text)
        for item in found:
            self.artifact_index.add(item)

    def get_ground_truth_prompt(self) -> str:
        """Generates a grounding reminder based on the artifact index."""
        if not self.artifact_index:
            return "No verified artifacts consolidated yet."
        
        items = "\n- ".join(sorted(list(self.artifact_index)))
        return f"CONFIRMED ARTIFACTS (Ground Truth):\n- {items}\n\nIMPORTANT: Use these verified facts to avoid hallucinations."

    # --- PILAR 3: STRATEGIC DELIBERATION ---
    def get_planning_prompt(self, goal: str, context: str) -> str:
        """Generates a prompt to force the agent to deliberate before using tools."""
        return (
            f"GOAL: {goal}\n"
            f"CONTEXT: {context}\n\n"
            "INSTRUCTION: Before taking any action, develop a 2-sentence technical plan. "
            "Focus on efficiency and evidence collection. Do not use tools yet."
        )

    # --- PILAR 4: CONTEXT MONITORING ---
    def track_turn(self) -> Dict[str, Any]:
        """Tracks turn counts and session health."""
        self.turn_count += 1
        return {
            "session_id": self.session_id,
            "turns": self.turn_count,
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "artifacts_found": len(self.artifact_index)
        }

    # --- PERSISTENCE HELPERS ---
    def export_session_state(self) -> Dict[str, Any]:
        """Exports the harness state for persistence."""
        return {
            "session_id": self.session_id,
            "artifact_index": list(self.artifact_index),
            "turn_count": self.turn_count,
            "hashes": list(self.action_history_hashes)
        }

    @classmethod
    def load_session_state(cls, state: Dict[str, Any]) -> 'UniversalAgentHarness':
        """Restores a harness from a saved state."""
        harness = cls(state["session_id"])
        harness.artifact_index = set(state.get("artifact_index", []))
        harness.turn_count = state.get("turn_count", 0)
        harness.action_history_hashes = set(state.get("hashes", []))
        return harness

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    # Initialize Harness
    harness = UniversalAgentHarness(session_id="user_123")
    
    # 1. Deliberation Phase
    print(harness.get_planning_prompt("Investigate IP 1.1.1.1", "High traffic detected"))
    
    # 2. Tool Call with Loop Detection
    tool = "whois"
    args = {"ip": "1.1.1.1"}
    
    if harness.check_loop(tool, args):
        print("Loop Detected! Aborting action.")
    else:
        print(f"Executing {tool}...")
        
    # 3. Artifact Indexing
    agent_output = "I found evidence EV_LOG_998 in the server logs."
    harness.extract_and_index(agent_output)
    print(harness.get_ground_truth_prompt())
    
    # 4. Turn Tracking
    print(harness.track_turn())
