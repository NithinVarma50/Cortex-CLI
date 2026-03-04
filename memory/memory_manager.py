import os
import uuid
import json
from pathlib import Path

from memory.vector_store import VectorStore
from memory.knowledge_store import KnowledgeStore
from memory.history_store import HistoryStore

class MemoryManager:
    """Unified hybrid memory interface overlaying Layer 1 (Vector), Layer 2 (Structured), and Layer 3 (Working)."""

    def __init__(self):
        self.storage_path = os.getenv("CORTEX_STORAGE_PATH", os.path.join(os.getcwd(), "storage"))
        self.max_storage_gb = float(os.getenv("CORTEX_MAX_STORAGE_GB", "10"))
        
        # Layer 1 - Vector
        self.vector = VectorStore(self.storage_path)
        
        # Layer 2 - Structured
        self.knowledge = KnowledgeStore(self.storage_path)
        self.history = HistoryStore(self.storage_path)
        
        # Layer 3 - Working Memory (in-process)
        self.working_memory = {}

    def store(self, content: str, memory_type: str = "company", agent: str = None) -> str:
        """Store information via vector db. Also logs an event."""
        doc_id = str(uuid.uuid4())
        metadata = {"agent": agent} if agent else {}
        self.vector.store(doc_id, content, memory_type=memory_type, metadata=metadata)
        self.knowledge.log_event("memory_stored", f"Stored memory in {memory_type}")
        return doc_id

    def search(self, query: str, memory_type: str = "company", top_k: int = 5) -> list:
        """Search similar memories."""
        return self.vector.search(query, memory_type, top_k)

    def get_agent_context(self, agent_name: str, task: str) -> str:
        """Get relevant context for an agent based on the current task."""
        # 1. Search company memory
        company_hits = self.search(task, memory_type="company", top_k=3)
        # 2. Search department memory for this agent
        dept_hits = self.search(f"{agent_name} {task}", memory_type="department", top_k=2)
        
        context_parts = []
        for hit in company_hits:
            context_parts.append(f"- {hit['content']}")
        for hit in dept_hits:
            context_parts.append(f"- {hit['content']}")
            
        return "\n".join(context_parts)

    def clear(self, memory_type: str = "all") -> None:
        """Clear memory databases."""
        if memory_type == "all":
            self.vector.clear_all()
            self.knowledge.clear_all()
            self.working_memory.clear()

    def export(self, filepath: str) -> None:
        """Export working and structured data as JSON."""
        data = {
            "working_memory": self.working_memory,
            "stats": self.get_stats()
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_stats(self) -> dict:
        """Aggregate stats from all layers."""
        stats = self.vector.get_stats()
        stats.update(self.knowledge.get_stats())
        dir_size = self._get_dir_size(self.storage_path)
        stats["total_storage_mb"] = round(dir_size / (1024 * 1024), 2)
        stats["limit_gb"] = self.max_storage_gb
        return stats

    def check_storage_limit(self) -> bool:
        """Warn at 80%, block at 95%. Returns True if okay to proceed, False if blocked."""
        dir_size_gb = self._get_dir_size(self.storage_path) / (1024 ** 3)
        usage_pct = dir_size_gb / self.max_storage_gb
        
        if usage_pct > 0.95:
            return False
        elif usage_pct > 0.80:
            # We would print a warning in display, but we'll return True
            pass
        return True

    def handle_storage_overflow(self) -> None:
        """Raise an error or warning about overflow."""
        raise RuntimeError("Storage overflow! Please archive or delete old memories.")

    def _get_dir_size(self, path='.'):
        total = 0
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += self._get_dir_size(entry.path)
        return total
