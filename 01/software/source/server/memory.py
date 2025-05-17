import os
import json
from datetime import datetime

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory_storage.json")

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"conversations": []}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

def add_to_memory(user_message, assistant_response):
    memory = load_memory()
    memory["conversations"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "user": user_message,
        "assistant": assistant_response
    })
    save_memory(memory)
