import random
from collections import deque
from db.models import waifus

RARITY_WEIGHTS = {
    "Common": 75.47,
    "Uncommon": 53.76,
    "Rare": 42.89,
    "Legendary": 24.82,
    "Special": 15.67,
    "Celestial": 8.43,
    "AMV": 2.98,
}

DECAY_BUFFER = deque(maxlen=24)

def pick_random_waifu():
    all_waifus = list(waifus.find({}))
    if not all_waifus:
        return None

    rarities = list(RARITY_WEIGHTS.keys())
    weights = list(RARITY_WEIGHTS.values())
    chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]

    candidates = [w for w in all_waifus if w["rarity"].lower() == chosen_rarity.lower()]

    if chosen_rarity in ["Common", "Uncommon", "Rare"]:
        candidates = [w for w in candidates if w["id"] not in DECAY_BUFFER]

    if not candidates:
        candidates = [w for w in all_waifus if w["rarity"].lower() == chosen_rarity.lower()]

    chosen = random.choice(candidates)

    if chosen_rarity in ["Common", "Uncommon", "Rare"]:
        DECAY_BUFFER.append(chosen["id"])

    return chosen
    
