import sqlite3
from dataclasses import dataclass
from typing import Optional
from config import DB_PATH


@dataclass
class Pokemon:
    id:          int
    name:        str
    type1:       str
    type2:       Optional[str]
    height:      int   # decimetres
    weight:      int   # hectograms
    hp:          int
    attack:      int
    defense:     int
    speed:       int
    sp_attack:   int
    sp_defense:  int
    category:    str
    description: str
    sprite_path: Optional[str]
    cry_path:    Optional[str]

    @property
    def height_str(self) -> str:
        total_inches = round(self.height * 3.937)
        return f"{total_inches // 12}'{total_inches % 12:02d}\""

    @property
    def weight_str(self) -> str:
        return f"{self.weight / 4.536:.1f} lbs"

    @property
    def types(self) -> list[str]:
        return [t for t in (self.type1, self.type2) if t]


_conn: Optional[sqlite3.Connection] = None


def _get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH)
        _conn.row_factory = sqlite3.Row
    return _conn


def _row_to_pokemon(row) -> Pokemon:
    return Pokemon(**{k: row[k] for k in row.keys()})


def get_all() -> list[Pokemon]:
    rows = _get_conn().execute(
        "SELECT * FROM pokemon ORDER BY id"
    ).fetchall()
    return [_row_to_pokemon(r) for r in rows]


def get_by_id(poke_id: int) -> Optional[Pokemon]:
    row = _get_conn().execute(
        "SELECT * FROM pokemon WHERE id = ?", (poke_id,)
    ).fetchone()
    return _row_to_pokemon(row) if row else None


def search_by_name(query: str) -> list[Pokemon]:
    rows = _get_conn().execute(
        "SELECT * FROM pokemon WHERE name LIKE ? ORDER BY id",
        (f"%{query}%",),
    ).fetchall()
    return [_row_to_pokemon(r) for r in rows]


def is_populated() -> bool:
    try:
        count = _get_conn().execute("SELECT COUNT(*) FROM pokemon").fetchone()[0]
        return count > 0
    except Exception:
        return False
