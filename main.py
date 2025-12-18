import requests
import time

SCRYFALL_CARD_URL = "https://api.scryfall.com/cards/{}"
REQUEST_DELAY = 0.11  # seguro para rate limit

# ─────────────────────────────────────────────
# MODELO DE CARTA
# ─────────────────────────────────────────────

class Card:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.cmc = data.get("cmc", 0)
        self.colors = data.get("color_identity", [])
        self.type_line = data.get("type_line", "")
        self.text = data.get("oracle_text") or ""
        self.is_legendary = "Legendary" in self.type_line
        self.tags = set()
        self.score = 0

# ─────────────────────────────────────────────
# SCRYFALL
# ─────────────────────────────────────────────

def fetch_card(card_id):
    r = requests.get(SCRYFALL_CARD_URL.format(card_id))
    r.raise_for_status()
    time.sleep(REQUEST_DELAY)
    return r.json()

# ─────────────────────────────────────────────
# TAGGING
# ─────────────────────────────────────────────

TAG_RULES = {
    "ramp": [
        "add",
        "treasure",
        "search your library for a land"
    ],
    "draw": [
        "draw a card"
    ],
    "removal": [
        "destroy",
        "exile",
        "sacrifice"
    ],
    "counter": [
        "counter target"
    ],
    "tokens": [
        "create",
        "token"
    ],
    "+1/+1": [
        "+1/+1 counter"
    ],
    "sacrifice": [
        "sacrifice"
    ],
    "etb": [
        "enters the battlefield"
    ],
     "flashback": [
        "flashback"
    ],
    "exile": [
        "exile",
        "exiled",
        "exiles"
    ],
    "attack": [
        "attack",
        "attacks"
    ],
    "blocked": [
        "blocked"
    ],
    "cost_reduction_target": [
        "costs",
        "less to cast"
    ],
    "earthbend": [
        "earthbend"
    ],
    "firebend": [
        "firebend"
    ],
    "waterbend": [
        "waterbend"
    ],
    "airbend": [
        "airbend"
    ]
}

def tag_card(card):
    text = card.text.lower()
    for tag, keys in TAG_RULES.items():
        for k in keys:
            if k in text:
                card.tags.add(tag)
                break

# ─────────────────────────────────────────────
# COMANDANTE
# ─────────────────────────────────────────────

def commander_score(card):
    score = 0
    if card.is_legendary and "Creature" in card.type_line:
        score += 5
    score += len(card.tags) * 2
    return score

def choose_commander(cards):
    candidates = [
        c for c in cards
        if c.is_legendary and "Creature" in c.type_line
    ]
    if not candidates:
        raise RuntimeError("No hay comandante legal en la colección.")
    return max(candidates, key=commander_score)

# ─────────────────────────────────────────────
# EFECTOS ESPECIALES DEL COMANDANTE
# ─────────────────────────────────────────────

COMMANDER_EFFECTS = {
    "double_etb": [
        "trigger an additional time",
        "triggers an additional time",
        "enters the battlefield causes",
    ],
    "attack_triggers": [
        "whenever a creature attacks"
    ],
    "proliferate": [
        "proliferate"
    ],
    "cost_reduction": [
        "less to cast",
        "costs less"
    ],
    "flashback": [
        "flashback"
    ],
    "exile_matters": [
        "exile",
        "exiled",
        "exiles"
    ],
    "earthbend": [
        "earthbend"
    ],
    "firebend": [
        "firebend"
    ],
    "waterbend": [
        "waterbend"
    ],
    "airbend": [
        "airbend"
    ],
    "blocked_matters": [
        "blocked"
    ],
}


def detect_commander_effects(commander):
    effects = set()
    text = commander.text.lower()
    for effect, keys in COMMANDER_EFFECTS.items():
        if any(k in text for k in keys):
            effects.add(effect)
    return effects

# ─────────────────────────────────────────────
# ARQUETIPO
# ─────────────────────────────────────────────

def detect_archetype(cards):
    counter = {}
    for c in cards:
        for tag in c.tags:
            counter[tag] = counter.get(tag, 0) + 1
    return sorted(counter, key=counter.get, reverse=True)[:3]

# ─────────────────────────────────────────────
# SCORING
# ─────────────────────────────────────────────

def score_card(card, archetype, commander, effects):
    score = 0

    # sinergia con arquetipo general
    for tag in archetype:
        if tag in card.tags:
            score += 3

    # roles básicos
    if "ramp" in card.tags:
        score += 2
    if "draw" in card.tags:
        score += 2
    if "removal" in card.tags:
        score += 2

    # ───────── SINERGIAS AVANZADAS AUTOMÁTICAS ─────────
    BONUS_EFFECT_SCORE = 4

    for effect, keywords in COMMANDER_EFFECTS.items():
        if effect in effects:
            # revisa tags primero
            if any(k.lower() in card.tags for k in keywords):
                score += BONUS_EFFECT_SCORE
                continue  # ya sumó, no hace falta revisar texto
            # revisa texto de la carta
            text_lower = card.text.lower()
            if any(k.lower() in text_lower for k in keywords):
                score += BONUS_EFFECT_SCORE

    # curva
    if card.cmc <= 3:
        score += 1

    

    card.score = score


# ─────────────────────────────────────────────
# CONSTRUCCIÓN DEL MAZO
# ─────────────────────────────────────────────

def build_deck(cards, commander):
    legal_cards = [
        c for c in cards
        if c.id != commander.id
        and set(c.colors).issubset(set(commander.colors))
    ]

    archetype = detect_archetype(legal_cards)
    effects = detect_commander_effects(commander)

    for c in legal_cards:
        score_card(c, archetype, commander, effects)

    deck = []

    role_targets = {
        "ramp": 10,
        "draw": 8,
        "removal": 8,
    }

    for role, target in role_targets.items():
        pool = sorted(
            [c for c in legal_cards if role in c.tags],
            key=lambda c: c.score,
            reverse=True
        )
        for c in pool:
            if c not in deck and len(deck) < target:
                deck.append(c)

    remaining = sorted(
        [c for c in legal_cards if c not in deck],
        key=lambda c: c.score,
        reverse=True
    )

    for c in remaining:
        if len(deck) < 63:
            deck.append(c)

    return deck, archetype

# ─────────────────────────────────────────────
# TIERRAS
# ─────────────────────────────────────────────

BASIC_LANDS = {
    "W": "Plains",
    "U": "Island",
    "B": "Swamp",
    "R": "Mountain",
    "G": "Forest",
}

def average_cmc(cards):
    return sum(c.cmc for c in cards) / max(len(cards), 1)

def count_ramp(cards):
    return sum(1 for c in cards if "ramp" in c.tags)

def generate_lands(deck, commander):
    lands = []
    base = 36

    if average_cmc(deck) > 3.5:
        base += 1
    if count_ramp(deck) >= 12:
        base -= 1

    base = max(34, min(base, 38))

    colors = commander.colors
    if not colors:
        return ["Wastes"] * base

    per = base // len(colors)
    rem = base % len(colors)

    for c in colors:
        lands.extend([BASIC_LANDS[c]] * per)
    for i in range(rem):
        lands.append(BASIC_LANDS[colors[i]])

    return lands

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    with open("scryfall_ids.txt") as f:
        ids = [l.strip() for l in f if l.strip()]

    print(f"Cargando {len(ids)} cartas...\n")

    cards = []
    total = len(ids)
    i=0
    for cid in ids:
        i += 1
        data = fetch_card(cid)
        card = Card(data)
        print(f"\rCargando {i}/{total} - {card.name} ({', '.join(card.colors) or 'Incoloro'})", end="")

        tag_card(card)
        cards.append(card)

    commander = choose_commander(cards)
    deck, archetype = build_deck(cards, commander)
    lands = generate_lands(deck, commander)

    print("══════════════════════════════════════")
    print(f"COMANDANTE: {commander.name}")
    print(f"COLORES: {', '.join(commander.colors) or 'Incoloro'}")
    print(f"ARQUETIPO: {', '.join(archetype)}")
    print("══════════════════════════════════════\n")

    print("MAZO:\n")
    print(f"1 {commander.name}\n")

    for c in deck:
        print(f"1 {c.name}")

    for land in lands:
        print(f"1 {land}")

    print("\n✔ Mazo Commander (100 cartas) generado.")

if __name__ == "__main__":
    main()
