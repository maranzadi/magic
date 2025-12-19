import json
import os


with open("cards.json", "r", encoding="utf-8") as f:
    CARD_DB = json.load(f)

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
        self.score_breakdown = {}

        
        main_types = self.type_line.split("—")[0]  # antes del —
        self.types = set(main_types.strip().split())

        self.image_url = self._get_image_url(data)

    def _get_image_url(self, data):
        # Carta normal
        if "image_uris" in data:
            return data["image_uris"].get("normal")

        # Carta de doble cara
        if "card_faces" in data and data["card_faces"]:
            face = data["card_faces"][0]
            if "image_uris" in face:
                return face["image_uris"].get("normal")

        return None

# ─────────────────────────────────────────────
# SCRYFALL
# ─────────────────────────────────────────────

def fetch_card(card_id):
    if card_id not in CARD_DB:
        raise KeyError(f"Carta con id {card_id} no encontrada en cards.json")

    data = CARD_DB[card_id]

    return {
        "id": data["id"],
        "name": data["name"],
        "cmc": data.get("cmc", 0),
        "color_identity": data.get("colors", []),
        "type_line": data.get("type_line", ""),
        "oracle_text": data.get("text", ""),
    }

def add_score(card, reason, value):
    card.score += value
    card.score_breakdown[reason] = card.score_breakdown.get(reason, 0) + value

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
        "+1/+1 counter",
        "+1/+0",
        "+2/+0",
        "+1/+2",
        "+2/+2",
        "+0/+2",
        "counter",
        "counters"
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
    ],
    "land": [
        "land",
        "landfall",
        "Landfall"
    ],
    "landfall": [
        "land",
        "landfall",
        "Landfall"
    ],
    "lander": [
        "lander"  # nueva tag para la habilidad lander
    ],
    "artifact":[
        "artifacts",
        "artifatc"
    ],
    "ally":[
        "ally",
        "Ally"
    ]
}

def tag_card(card):
    text = card.text.lower()
    for tag, keys in TAG_RULES.items():
        for k in keys:
            if k in text:
                card.tags.add(tag)
                break
    
     # ───── Tags por TYPE_LINE ─────
    if "Artifact" in card.type_line:
        card.tags.add("artifact")

    if "Land" in card.type_line:
        card.tags.add("land")

    if "Artifact Land" in card.type_line:
        card.tags.add("artifact")
        card.tags.add("land")
    
    if "Ally" in card.type_line:
        card.tags.add("ally")

# ─────────────────────────────────────────────
# COMANDANTE
# ─────────────────────────────────────────────

def choose_commander_manual(cards):
    candidates = [c for c in cards if c.is_legendary and "Creature" in c.type_line]
    if not candidates:
        raise RuntimeError("No hay comandante legal en la colección.")

    print("Elige tu comandante:")
    for i, c in enumerate(candidates, start=1):
        print(f"{i}. {c.name} ({', '.join(c.colors) or 'Incoloro'})")

    while True:
        choice = input(f"Ingrese el número (1-{len(candidates)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(candidates):
            return candidates[int(choice)-1]
        print("Opción inválida, intenta de nuevo.")

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
    "land": [
        "land"
    ],
    "artifact_matters": [
        "artifact"
    ],
    "ally": [
        "ally"
    ]

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

def score_card(card, archetype, commander, effects, deck=None):
    card.score = 0
    card.score_breakdown = {}

    # legalidad de color
    if set(card.colors).issubset(set(commander.colors)):
        add_score(card, "color_identity", 2)
    else:
        add_score(card, "color_mismatch", -1000)
        return

    # sinergia con arquetipo
    for tag in archetype:
        if tag in card.tags:
            add_score(card, f"archetype_{tag}", 3)

    # roles básicos
    if "ramp" in card.tags:
        add_score(card, "ramp_role", 2)
    if "draw" in card.tags:
        add_score(card, "draw_role", 2)
    if "removal" in card.tags:
        add_score(card, "removal_role", 2)

    # comandante
    BONUS = 20
    for effect, keywords in COMMANDER_EFFECTS.items():
        if effect in effects:
            if effect.replace("_matters", "") in card.tags:
                add_score(card, f"commander_{effect}", BONUS)
            elif any(k in card.text.lower() for k in keywords):
                add_score(card, f"commander_text_{effect}", BONUS)

    # curva
    if card.cmc <= 3:
        add_score(card, "low_cmc", 1)

    # combos
    if deck:
        for combo in detect_dynamic_combos(deck, effects):
            if card.name in combo["cards"]:
                add_score(card, f"combo_{combo['type']}", combo["bonus_score"])



DYNAMIC_COMBOS = {
    # "etb_synergy": ["etb", "double_etb"],
    # "proliferate_synergy": ["proliferate", "+1/+1"],
    # "ramp_synergy": ["ramp", "cost_reduction_target"],
    # "sacrifice_synergy": ["sacrifice", "etb"],
    "lands_artifacts_ramp_synergy": ["land", "artifact", "landfall"]
}


def detect_dynamic_combos(deck, commander_effects):
    combos = []
    # Revisamos pares de cartas en el deck
    for i, card1 in enumerate(deck):
        for card2 in deck[i+1:]:
            for combo_name, tags in DYNAMIC_COMBOS.items():
                # Si alguna carta tiene un tag y la otra tiene el efecto correspondiente
                if (card1.tags & set(tags)) and (card2.tags & set(tags)):
                    # Registrar el combo
                    combos.append({
                        "cards": [card1.name, card2.name],
                        "type": combo_name,
                        "bonus_score": 5
                    })
                # También combinaciones con efectos del comandante
                if (card1.tags & set(tags)) and (set(tags) & commander_effects):
                    combos.append({
                        "cards": [card1.name],
                        "type": f"{combo_name}_commander",
                        "bonus_score": 14
                    })
    return combos

# ─────────────────────────────────────────────
# CONSTRUCCIÓN DEL MAZO
# ─────────────────────────────────────────────

def build_deck(cards, commander):
    legal_cards = [c for c in cards if set(c.colors).issubset(set(commander.colors))]
    archetype = detect_archetype(legal_cards)
    effects = detect_commander_effects(commander)

    # Calcular score inicial sin combos
    for c in legal_cards:
        score_card(c, archetype, commander, effects)

    deck = []

    # Rellenar roles básicos
    role_targets = {"ramp": 10, "draw": 8, "removal": 8}
    for role, target in role_targets.items():
        pool = sorted([c for c in legal_cards if role in c.tags], key=lambda c: c.score, reverse=True)
        for c in pool:
            if c not in deck and len(deck) < target:
                deck.append(c)

    # Agregar cartas restantes por score
    remaining = sorted([c for c in legal_cards if c not in deck], key=lambda c: c.score, reverse=True)
    for c in remaining:
        if len(deck) < 63:
            deck.append(c)

    # ───────── Optimización iterativa para combos ─────────
    deck = optimize_deck(deck, legal_cards, archetype, commander, effects, max_size=63)

    return deck, archetype



def optimize_deck(deck, legal_cards, archetype, commander, effects, max_size=63):
    """
    Optimiza un deck reemplazando cartas de menor score por otras mejores.
    """
    # Recalcular scores con combos dinámicos
    for c in legal_cards:
        score_card(c, archetype, commander, effects, deck=deck)

    # Ordenar todas las cartas legales por score descendente
    legal_sorted = sorted(legal_cards, key=lambda c: c.score, reverse=True)

    # Inicializar el deck final
    final_deck = list(deck)

    # Iterar mientras haya cartas fuera del deck que sean mejores que las peores dentro
    improved = True
    while improved:
        improved = False
        # Carta con menor score dentro del deck
        worst_in_deck = min(final_deck, key=lambda c: c.score)
        # Carta con mayor score fuera del deck
        for candidate in legal_sorted:
            if candidate not in final_deck and candidate.score > worst_in_deck.score:
                # Reemplazar
                final_deck.remove(worst_in_deck)
                final_deck.append(candidate)
                improved = True
                break  # recalcular después de un cambio

        if improved:
            # Recalcular scores porque los combos pueden cambiar
            for c in legal_cards:
                score_card(c, archetype, commander, effects, deck=final_deck)

    # Asegurar tamaño máximo
    return final_deck[:max_size]

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
    ids = list(CARD_DB.keys())


    print(f"Cargando {len(ids)} cartas...\n")

    cards = []
    total = len(ids)
    i = 0
    for cid in ids:
        i += 1
        data = fetch_card(cid)
        card = Card(data)
        tag_card(card)
        cards.append(card)
        print(f"\rCargando {i}/{total} - {card.name} - {card.score} ({', '.join(card.colors) or 'Incoloro'})", end="")


    commander = choose_commander_manual(cards)
    deck, archetype = build_deck(cards, commander)
    lands = generate_lands(deck, commander)

    print("\n══════════════════════════════════════")
    print(f"COMANDANTE: {commander.name}")
    print(f"COLORES: {', '.join(commander.colors) or 'Incoloro'}")
    print(f"ARQUETIPO: {', '.join(archetype)}")
    print("══════════════════════════════════════\n")

    print("MAZO:\n")
    print(f"1 {commander.name}\n")

    for c in deck:
        print(f"1 {c.name} - {', '.join(sorted(c.types))} - {c.score}")

    for land in lands:
        print(f"1 {land}")

    print("\n✔ Mazo Commander (100 cartas) generado.")

    ruta = "./webPage/src/decks/"
    os.makedirs(ruta, exist_ok=True)

    file_path = os.path.join(ruta, f"{commander.name}.json")

    deck_ids = {c.id for c in deck}

    output = {
        "commander": {
            "id": commander.id,
            "name": commander.name,
            "colors": commander.colors,
            "score": commander.score,
            "score_breakdown": getattr(commander, "score_breakdown", {}),
            "commander_tags": list(commander.tags)
        },
        "deck": [],
        "lands": lands,
        "other_cards": []
    }

    # Guardar cartas del deck
    for c in deck:
        output["deck"].append({
            "id": c.id,
            "name": c.name,
            "score": c.score,
            "score_breakdown": getattr(c, "score_breakdown", {}),
            "included": True
        })

    # Guardar las demás cartas
    for c in cards:
        if c.id not in deck_ids:
            output["other_cards"].append({
                "id": c.id,
                "name": c.name,
                "score": c.score,
                "score_breakdown": getattr(c, "score_breakdown", {}),
                "included": False
            })

    # Guardar todo en JSON
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

                    
                        

if __name__ == "__main__":
    main()
