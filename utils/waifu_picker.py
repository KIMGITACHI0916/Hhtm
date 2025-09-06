import json
import random

def load_waifus():
    with open("waifu_data/waifus.json", "r") as f:
        return json.load(f)

def pick_random_waifu():
    waifus = load_waifus()
    return random.choice(waifus)
