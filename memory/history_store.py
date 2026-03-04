import os
from sqlite_utils import Database

class HistoryStore:
    """Manages workflow and task execution history (SQLite)."""

    def __init__(self, storage_path: str):
        os.makedirs(storage_path, exist_ok=True)
        self.db_path = os.path.join(storage_path, "cortex.db")
        self.db = Database(self.db_path)
        
        if "workflows" not in self.db.table_names():
            self.db["workflows"].create({
                "run_id": str,
                "name": str,
                "status": str,
                "started_at": str,
                "completed_at": str
            }, pk="run_id")

        if "tasks" not in self.db.table_names():
            self.db["tasks"].create({
                "task_id": str,
                "run_id": str,
                "agent": str,
                "task": str,
                "result": str,
                "status": str,
                "started_at": str,
                "completed_at": str
            }, pk="task_id")

    def create_workflow_run(self, run_id: str, name: str):
        import datetime
        self.db["workflows"].insert({
            "run_id": run_id,
            "name": name,
            "status": "running",
            "started_at": datetime.datetime.now().isoformat(),
            "completed_at": None
        })

    def update_workflow_run(self, run_id: str, status: str):
        import datetime
        self.db["workflows"].update(run_id, {
            "status": status,
            "completed_at": datetime.datetime.now().isoformat() if status in ["completed", "failed"] else None
        })

    def log_task(self, task_id: str, run_id: str, agent: str, task: str):
        import datetime
        self.db["tasks"].insert({
            "task_id": task_id,
            "run_id": run_id,
            "agent": agent,
            "task": task,
            "result": None,
            "status": "running",
            "started_at": datetime.datetime.now().isoformat(),
            "completed_at": None
        })

    def update_task_result(self, task_id: str, status: str, result: str):
        import datetime
        self.db["tasks"].update(task_id, {
            "status": status,
            "result": result,
            "completed_at": datetime.datetime.now().isoformat()
        })
