import os
import json
from pathlib import Path
from src.config import BASE_DIR

REGISTRY_FILE = BASE_DIR / "_memories_index.json"

class Registry:
    def __init__(self):
        self.file_path = REGISTRY_FILE
        self._ensure_registry()

    def _ensure_registry(self):
        """Creates the registry file if it doesn't exist."""
        if not self.file_path.exists():
            self._save({"entities": {}})

    def _load(self):
        """Loads the registry JSON."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"entities": {}}

    def _save(self, data):
        """Saves data to the registry JSON."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def find_entity(self, name):
        """
        Looks up an entity by name (case-insensitive).
        Returns the entity dict or None.
        """
        data = self._load()
        name_lower = name.lower()
        
        # Direct lookup
        for key, val in data.get("entities", {}).items():
            if key.lower() == name_lower:
                return val
            # Check aliases if implemented later
        return None

    def get_all_entities_summary(self):
        """Returns a concise list of known entities for AI context."""
        data = self._load()
        summary_list = []
        for key, val in data.get("entities", {}).items():
            summary_list.append(f"{val['entity_name']} ({val['folder']}) - {val.get('summary', '')}")
        return "\n".join(summary_list)

    def add_entity(self, name, folder, filepath, summary="", type="entity"):
        """Registers a new entity."""
        data = self._load()
        # Use lowercase key for normalization
        key = name.lower()
        
        data["entities"][key] = {
            "entity_name": name,
            "type": type,
            "folder": folder,
            "file": str(filepath), # Store relative path string or full path? Spec says "Apps/Grammarly.md"
            "summary": summary,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        self._save(data)

    def update_entity_timestamp(self, name):
        """Updates the last_updated field."""
        data = self._load()
        key = name.lower()
        if key in data["entities"]:
            data["entities"][key]["last_updated"] = datetime.now().isoformat()
            self._save(data)

from datetime import datetime
