import os
from database.adapters.sqlite_adapter import SQLiteAdapter
from database.adapters.json_adapter import JSONAdapter  

class Database:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            adapter_type = os.getenv("OFICINA_DB_ADAPTER", "sqlite")
            if adapter_type == "sqlite":
                cls._instance = SQLiteAdapter("oficina.db")
            else:
                cls._instance = JSONAdapter("database/json_store")
        return cls._instance