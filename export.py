import csv
import json
import os
import time
import requests
import shutil


# =========================
# CONFIG
# =========================

mainFile = "ManaBox_Collection.csv"
JSON_FILE = "cards.json"
JSON_FILE2 = "./webPage/src/"
SCRYFALL_API = "https://api.scryfall.com/cards/{}"

REQUIRED_FIELDS = {
    "id",
    "name",
    "cmc",
    "colors",
    "type_line",
    "types",
    "text",
    "is_legendary",
    "image_url"
}

# =========================
# CARD CLASS
# =========================

class Card:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.cmc = data.get("cmc", 0)
        self.colors = data.get("colors", [])
        self.type_line = data.get("type_line", "")
        self.text = data.get("text", "")
        self.is_legendary = data.get("is_legendary", False)
        self.types = set(data.get("types", []))
        self.image_url = data.get("image_url")
        self.tags = set()
        self.score = 0


# =========================
# JSON CACHE
# =========================

def load_cards_db():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cards_db(db):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def copi():
    origen = JSON_FILE

    # Archivo destino
    destino = JSON_FILE2

    # Copiar
    shutil.copy(origen, destino)

    print("Archivo copiado correctamente")

# =========================
# SCRYFALL
# =========================

def fetch_card(scryfall_id):
    time.sleep(0.1)  # respetar rate limit
    r = requests.get(SCRYFALL_API.format(scryfall_id), timeout=10)
    r.raise_for_status()
    return r.json()


def card_data_from_api(data):
    type_line = data.get("type_line", "")
    main_types = type_line.split("—")[0].strip().split()

    # Imagen
    image_url = None
    if "image_uris" in data:
        image_url = data["image_uris"].get("normal")
    elif "card_faces" in data and data["card_faces"]:
        image_url = data["card_faces"][0].get("image_uris", {}).get("normal")

    return {
        "id": data["id"],
        "name": data["name"],
        "cmc": data.get("cmc", 0),
        "colors": data.get("color_identity", []),
        "type_line": type_line,
        "types": main_types,
        "text": data.get("oracle_text") or "",
        "is_legendary": "Legendary" in type_line,
        "image_url": image_url
    }


# =========================
# CACHE LOGIC
# =========================

def get_card_cached(scryfall_id, cards_db):
    card = cards_db.get(scryfall_id)

    # No existe
    if card is None:
        print(f"⬇️ Descargando carta {scryfall_id}")
        api_data = fetch_card(scryfall_id)
        card = card_data_from_api(api_data)
        cards_db[scryfall_id] = card
        return card

    # Existe, pero ¿está completa?
    missing = REQUIRED_FIELDS - card.keys()
    if missing:
        print(f"🔄 Actualizando {scryfall_id}, faltan: {missing}")
        api_data = fetch_card(scryfall_id)
        card.update(card_data_from_api(api_data))
        cards_db[scryfall_id] = card

    return card


# =========================
# MAIN
# =========================

def main():
    cards_db = load_cards_db()
    cards = []

    with open(mainFile, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            scryfall_id = row.get("Scryfall ID")
            if not scryfall_id:
                continue

            card_data = get_card_cached(scryfall_id, cards_db)
            card = Card(card_data)
            cards.append(card)

            print(f"\rCargada: {card.name}", end="")

    save_cards_db(cards_db)
    copi()
    print("\n✅ Proceso completado")


if __name__ == "__main__":
    main()
