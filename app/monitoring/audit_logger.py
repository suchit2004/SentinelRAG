import json
import os
from datetime import datetime

class AuditLogger:
    def __init__(self, log_path: str = None):
        if log_path is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            self.log_path = os.path.join(base_dir, "data", "security_audit.jsonl")
        else:
            self.log_path = log_path

    def log_interaction(self, query: str, username: str, role_name: str, input_is_safe: bool, safety_reason: str, pii_detected: bool, pii_types: list, latency_ms: float):
        """
        Logs a single RAG pipeline interaction to the security audit log.
        """
        try:
            # Ensure parent directories exist
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "username": username,
                "role": role_name,
                "query": query,
                "input_is_safe": input_is_safe,
                "safety_reason": safety_reason,
                "pii_detected": pii_detected,
                "pii_types": pii_types,
                "latency_ms": round(latency_ms, 2)
            }
            
            with open(self.log_path, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Failed to write audit log: {e}")

    def read_logs(self) -> list:
        """
        Reads and returns all logged interactions.
        """
        if not os.path.exists(self.log_path):
            return []
            
        logs = []
        try:
            with open(self.log_path, "r") as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line.strip()))
            # Sort newest first
            logs.reverse()
            return logs
        except Exception as e:
            print(f"Error reading audit logs: {e}")
            return []

    def clear_logs(self) -> bool:
        """
        Deletes all logged interactions.
        """
        try:
            if os.path.exists(self.log_path):
                os.remove(self.log_path)
            return True
        except Exception as e:
            print(f"Error clearing logs: {e}")
            return False
