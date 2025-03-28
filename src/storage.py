import json
import os

SAVE_FILE = "chat_rooms.json"

def load_rooms():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as file:
            data = json.load(file)
            for room in data.values():
                for msg in room:
                    if "reactions" in msg and isinstance(msg["reactions"], list):
                        msg["reactions"] = {}
            return data
    return {}

def save_rooms(rooms):
    with open(SAVE_FILE, "w") as file:
        json.dump(rooms, file)