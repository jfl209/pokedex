"""
One-time setup script: pulls Gen-1 data from PokeAPI and stores it locally.

Usage:
    python -m data.fetch
"""

import os
import sys
import time
import sqlite3
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH, SPRITES_DIR, CRIES_DIR

GEN1_COUNT = 151
API_BASE   = "https://pokeapi.co/api/v2"
DELAY      = 0.3   # seconds between requests to be polite to the free API


def _get(url: str) -> dict:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def _download(url: str, dest: str) -> bool:
    if os.path.exists(dest):
        return True
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        with open(dest, "wb") as f:
            f.write(r.content)
        return True
    except Exception as e:
        print(f"  warn: could not download {url}: {e}")
        return False


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pokemon (
            id          INTEGER PRIMARY KEY,
            name        TEXT    NOT NULL,
            type1       TEXT    NOT NULL,
            type2       TEXT,
            height      INTEGER,
            weight      INTEGER,
            hp          INTEGER,
            attack      INTEGER,
            defense     INTEGER,
            speed       INTEGER,
            sp_attack   INTEGER,
            sp_defense  INTEGER,
            category    TEXT,
            description TEXT,
            sprite_path TEXT,
            cry_path    TEXT
        )
    """)
    conn.commit()


def fetch_description(species_url: str) -> tuple[str, str]:
    """Returns (category, english_flavor_text)."""
    data = _get(species_url)
    category = ""
    for g in data.get("genera", []):
        if g["language"]["name"] == "en":
            category = g["genus"]
            break
    description = ""
    for entry in data.get("flavor_text_entries", []):
        if entry["language"]["name"] == "en" and entry["version"]["name"] in ("red", "blue", "yellow"):
            description = entry["flavor_text"].replace("\n", " ").replace("\f", " ")
            break
    return category, description


def fetch_all() -> None:
    os.makedirs(SPRITES_DIR, exist_ok=True)
    os.makedirs(CRIES_DIR,   exist_ok=True)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    existing = {row[0] for row in conn.execute("SELECT id FROM pokemon")}

    for poke_id in range(1, GEN1_COUNT + 1):
        if poke_id in existing:
            print(f"  skip #{poke_id:03d} (already in db)")
            continue

        print(f"  fetch #{poke_id:03d}...", end=" ", flush=True)
        try:
            data = _get(f"{API_BASE}/pokemon/{poke_id}")
        except Exception as e:
            print(f"ERROR: {e}")
            continue

        name  = data["name"].capitalize()
        types = [t["type"]["name"] for t in data["types"]]
        type1 = types[0] if len(types) > 0 else ""
        type2 = types[1] if len(types) > 1 else None

        stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}

        # sprite (official front default)
        sprite_url  = (data["sprites"]["other"]["official-artwork"]["front_default"]
                       or data["sprites"]["front_default"])
        sprite_path = None
        if sprite_url:
            dest = os.path.join(SPRITES_DIR, f"{poke_id:03d}.png")
            if _download(sprite_url, dest):
                sprite_path = dest

        # cry (.ogg)
        cry_url  = data.get("cries", {}).get("latest") or data.get("cries", {}).get("legacy")
        cry_path = None
        if cry_url:
            ext  = ".ogg" if ".ogg" in cry_url else ".mp3"
            dest = os.path.join(CRIES_DIR, f"{poke_id:03d}{ext}")
            if _download(cry_url, dest):
                cry_path = dest

        # species endpoint for category + description
        time.sleep(DELAY)
        try:
            category, description = fetch_description(data["species"]["url"])
        except Exception:
            category, description = "", ""

        conn.execute(
            """INSERT OR REPLACE INTO pokemon
               (id, name, type1, type2, height, weight,
                hp, attack, defense, speed, sp_attack, sp_defense,
                category, description, sprite_path, cry_path)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                poke_id, name, type1, type2,
                data["height"], data["weight"],
                stats.get("hp"),      stats.get("attack"),
                stats.get("defense"), stats.get("speed"),
                stats.get("special-attack"), stats.get("special-defense"),
                category, description, sprite_path, cry_path,
            ),
        )
        conn.commit()
        print(f"{name}")
        time.sleep(DELAY)

    conn.close()
    print("Done.")


if __name__ == "__main__":
    fetch_all()
