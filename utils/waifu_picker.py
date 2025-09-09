import json
import pathlib
import random
from collections import deque

# JSON file with waifus
BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()
WAIFU_DATA = BASE_DIR / "waifu_data" / "waifus.json"

# rarity weights (probabilities)
RARITY_WEIGHTS = {
    "Common": 75.47,
    "Uncommon": 53.76,
    "Rare": 42.89,
    "Legendary": 24.82,
    "Special": 15.67,
    "Celestial": 8.43,
    "AMV": 2.98,
}

# decay buffer (stores recently dropped waifus)
DECAY_BUFFER = deque(maxlen=24)


def load_waifus():
    try:
        with open(WAIFU_DATA, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def pick_random_waifu():
    waifus = load_waifus()
    if not waifus:
        return None

    # weighted rarity selection
    rarities = list(RARITY_WEIGHTS.keys())
    weights = list(RARITY_WEIGHTS.values())
    chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]

    # filter waifus of that rarity
    candidates = [w for w in waifus if w["rarity"].lower() == chosen_rarity.lower()]
    if not candidates:
        return None

    # apply decay filter (only Common, Uncommon, Rare)
    if chosen_rarity in ["Common", "Uncommon", "Rare"]:
        candidates = [w for w in candidates if w["id"] not in DECAY_BUFFER]

    if not candidates:
        # fallback → pick random from all
        candidates = [w for w in waifus if w["rarity"].lower() == chosen_rarity.lower()]

    chosen = random.choice(candidates)

    # update decay buffer
    if chosen_rarity in ["Common", "Uncommon", "Rare"]:
        DECAY_BUFFER.append(chosen["id"])

    return chosen
    
