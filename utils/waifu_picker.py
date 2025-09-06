import json
import random
import os

WAIFU_FILE = os.path.join(os.path.dirname(__file__), "../waifu_data/waifus.json")

def load_waifus():
    with open(WAIFU_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_random_waifu():
    waifus = load_waifus()
    return random.choice(waifus)
