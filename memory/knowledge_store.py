import os
from sqlite_utils import Database


class KnowledgeStore:
    """Manages structured knowledge using SQLite (Layer 2)."""

    def __init__(self, storage_path: str):
        os.makedirs(storage_path, exist_ok=True)
        self.db_path = os.path.join(storage_path, "cortex.db")
        self.db = Database(self.db_path)
        
        # Initialize tables
        if "agents" not in self.db.table_names():
            self.db["agents"].create({
                "name": str,
                "role": str,
                "model": str,
                "skills": str, # JSON serialized list of skills
                "created_at": str
            }, pk="name")
            
        if "skills" not in self.db.table_names():
            self.db["skills"].create({
                "name": str,
                "installed_at": str
            }, pk="name")
            
        if "events" not in self.db.table_names():
            self.db["events"].create({
                "id": str,
                "type": str,
                "details": str,
                "timestamp": str
            }, pk="id")

    def insert_agent(self, name: str, role: str, model: str = "", skills: str = "[]"):
        import datetime
        self.db["agents"].upsert({
            "name": name, 
            "role": role, 
            "model": model,
            "skills": skills,
            "created_at": datetime.datetime.now().isoformat()
        }, pk="name")

    def update_agent(self, name: str, updates: dict):
        self.db["agents"].update(name, updates)

    def get_agent(self, name: str) -> dict:
        try:
            return next(self.db["agents"].rows_where("name = ?", [name]))
        except StopIteration:
            return None

    def list_agents(self) -> list[dict]:
        return list(self.db["agents"].rows)

    def log_event(self, event_type: str, details: str):
        import uuid
        import datetime
        self.db["events"].insert({
            "id": str(uuid.uuid4()),
            "type": event_type,
            "details": details,
            "timestamp": datetime.datetime.now().isoformat()
        })

    def clear_all(self):
        for table in ["agents", "skills", "events"]:
            if table in self.db.table_names():
                self.db[table].delete_where()

    def get_stats(self) -> dict:
        return {
            "agents_count": self.db["agents"].count if "agents" in self.db.table_names() else 0,
            "events_count": self.db["events"].count if "events" in self.db.table_names() else 0,
            "db_size_bytes": os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        }
