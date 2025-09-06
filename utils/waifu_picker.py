# utils/waifu_picker.py
import json
import os

def load_waifus():
    # Always resolve relative to the project root (/app/)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
    file_path = os.path.join(base_dir, "waifu_data", "waifus.json")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_random_waifu():
    import random
    waifus = load_waifus()
    return random.choice(waifus)
