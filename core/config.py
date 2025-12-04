# core/config.py

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
APP_ID = "io.github.brainvault.ai"
DATA_FILE = os.path.join(BASE_DIR, "brainvault_db.json")
CONFIG_FILE = os.path.join(BASE_DIR, "brainvault_config.json")
CSS_FILE = os.path.join(BASE_DIR, "assets", "style.css")


class ConfigManager:
    def __init__(self):
        self.config = {"api_key": ""}
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.config = json.load(f)
            except:
                pass

    def save(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f)
        except:
            pass

    def get_key(self):
        return self.config.get("api_key", "")

    def set_key(self, key):
        self.config["api_key"] = key
        self.save()