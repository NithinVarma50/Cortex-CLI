import os
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions


class VectorStore:
    """Manages semantic vector memory using ChromaDB."""

    def __init__(self, storage_path: str):
        self.db_path = os.path.join(storage_path, "vector_db")
        os.makedirs(self.db_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        # Using default SentenceTransformers embedding function
        self.embed_fn = embedding_functions.DefaultEmbeddingFunction()
        
        # Initialize default collections
        self.company_mem = self.client.get_or_create_collection(
            name="company_memory", embedding_function=self.embed_fn
        )
        self.dept_mem = self.client.get_or_create_collection(
            name="department_memory", embedding_function=self.embed_fn
        )
        self.workflow_hist = self.client.get_or_create_collection(
            name="workflow_history", embedding_function=self.embed_fn
        )

    def _get_collection(self, memory_type: str):
        if memory_type == "company":
            return self.company_mem
        elif memory_type == "department":
            return self.dept_mem
        elif memory_type == "workflow":
            return self.workflow_hist
        else:
            return self.company_mem

    def store(self, doc_id: str, content: str, memory_type: str = "company", metadata: dict = None):
        """Store text into specific vector collection."""
        collection = self._get_collection(memory_type)
        collection.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[doc_id]
        )

    def search(self, query: str, memory_type: str = "company", top_k: int = 5) -> list[dict]:
        """Search similar documents in vector store."""
        collection = self._get_collection(memory_type)
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Format results
        formatted_results = []
        if results and results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if 'distances' in results and results['distances'] else 0.0
                })
        return formatted_results

    def get_stats(self) -> dict:
        return {
            "company_memory_count": self.company_mem.count(),
            "department_memory_count": self.dept_mem.count(),
            "workflow_history_count": self.workflow_hist.count()
        }

    def clear_all(self):
        for name in ["company_memory", "department_memory", "workflow_history"]:
            try:
                self.client.delete_collection(name)
            except ValueError:
                pass
        # Re-create empty
        self.company_mem = self.client.get_or_create_collection(name="company_memory", embedding_function=self.embed_fn)
        self.dept_mem = self.client.get_or_create_collection(name="department_memory", embedding_function=self.embed_fn)
        self.workflow_hist = self.client.get_or_create_collection(name="workflow_history", embedding_function=self.embed_fn)
