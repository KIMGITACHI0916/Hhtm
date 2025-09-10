import random
from collections import deque
from db.models import waifus

# Weighted rarities
RARITY_WEIGHTS = {
    "Common": 75.47,
    "Uncommon": 53.76,
    "Rare": 42.89,
    "Legendary": 24.82,
    "Special": 15.67,
    "Celestial": 8.43,
    "AMV": 2.98,
}

# Decay buffer: recent common/uncommon/rare waifus
DECAY_BUFFER = deque(maxlen=24)

# Pity system: increases chance of rarer waifus if unlucky
USER_PITY = {}

def pick_random_waifu(user_id=None):
    all_waifus = list(waifus.find({}))
    if not all_waifus:
        return None

    rarities = list(RARITY_WEIGHTS.keys())
    weights = list(RARITY_WEIGHTS.values())

    # Apply pity for user
    if user_id and USER_PITY.get(user_id):
        pity_boost = USER_PITY[user_id]
        for i, r in enumerate(rarities):
            if r in ["Legendary", "Special", "Celestial", "AMV"]:
                weights[i] += pity_boost

    chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]

    candidates = [w for w in all_waifus if w["rarity"].lower() == chosen_rarity.lower()]

    # Apply decay buffer for common/uncommon/rare
    if chosen_rarity in ["Common", "Uncommon", "Rare"]:
        candidates = [w for w in candidates if w["id"] not in DECAY_BUFFER]

    # fallback if no candidates
    if not candidates:
        candidates = [w for w in all_waifus if w["rarity"].lower() == chosen_rarity.lower()]

    chosen = random.choice(candidates)

    # Update decay buffer
    if chosen_rarity in ["Common", "Uncommon", "Rare"]:
        DECAY_BUFFER.append(chosen["id"])

    # Update pity
    if user_id:
        if chosen_rarity in ["Legendary", "Special", "Celestial", "AMV"]:
            USER_PITY[user_id] = 0  # reset pity on rare drop
        else:
            USER_PITY[user_id] = USER_PITY.get(user_id, 0) + 2  # increase pity

    return chosen
                
