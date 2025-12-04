# core/database.py

import os
import json
import datetime
from .config import DATA_FILE 

class DataManager:
    def __init__(self):
        self.data = {"folders": []}
        self.load()

    def load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                    self._migrate()
            except:
                self.data = {"folders": []}
        if not self.data.get("folders"):
            self.create_folder("Загальні")

    def _migrate(self):
        changed = False
        for f in self.data.get("folders", []):
            for d in f.get("decks", []):
                for c in d.get("cards", []):
                    if "ease" not in c: c["ease"]=2.5; changed=True
                    if "interval" not in c: c["interval"]=1; changed=True
                    if "reps" not in c: c["reps"]=0; changed=True
        if changed: self.save()


    def save(self):
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except: pass


    def create_folder(self, name):
        f = {"id": str(datetime.datetime.now().timestamp()), "name": name, "decks": []}
        self.data["folders"].append(f); self.save()

    def delete_folder(self, fid):
        self.data["folders"] = [f for f in self.data["folders"] if f['id'] != fid]
        self.save()

    def create_deck(self, fid, name):
        for f in self.data["folders"]:
            if f["id"] == fid:
                d = {"id": str(datetime.datetime.now().timestamp()), "name": name, "cards": []}
                f["decks"].append(d); self.save(); return d

    def delete_deck(self, fid, did):
        for f in self.data["folders"]:
            if f["id"] == fid:
                f["decks"] = [d for d in f["decks"] if d["id"] != did]
                self.save(); return

    def add_card(self, fid, did, q, a):
        for f in self.data["folders"]:
            if f["id"] == fid:
                for d in f["decks"]:
                    if d["id"] == did:
                        c = {"id": str(datetime.datetime.now().timestamp()), "q": q, "a": a, "reps": 0, "interval": 1, "ease": 2.5}
                        d["cards"].append(c); self.save(); return True
        return False

    def delete_card(self, fid, did, cid):
        for f in self.data["folders"]:
            if f["id"] == fid:
                for d in f["decks"]:
                    if d["id"] == did:
                        d["cards"] = [c for c in d["cards"] if c["id"] != cid]
                        self.save(); return

    def update_stats(self, fid, did, cid, q):
        for f in self.data["folders"]:
            if f["id"] == fid:
                for d in f["decks"]:
                    if d["id"] == did:
                        for c in d["cards"]:
                            if c["id"] == cid:
                                if q >= 3: c["reps"]+=1; c["interval"]=int(c["interval"]*c["ease"])
                                else: c["reps"]=0; c["interval"]=1
                                self.save(); return

    def get_folders(self): 
        return self.data["folders"]