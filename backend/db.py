"""Shared SQLite access for the catalogue/inventory tables.

Used by both main.py (the /api/products routes) and tools.py (the agent's
product-lookup tools), so there is exactly one place that knows how to turn
a catalogue row + its inventory rows into a product dict.
"""

import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "data" / "campus_customs.db"
PRODUCTS_DIR = BASE_DIR / "data" / "data" / "products"

LOW_STOCK_THRESHOLD = 5  # a size at or below this (but > 0) counts as "low stock"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _low_stock_sizes(inventory: list[dict]) -> list[str]:
    return [item["size"] for item in inventory if 0 < item["quantity"] <= LOW_STOCK_THRESHOLD]


def serialize_product(row: sqlite3.Row, inventory: list[dict]) -> dict:
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "description": row["description"],
        "colors": json.loads(row["colors"]),
        "search_tags": json.loads(row["search_tags"]),
        "image_url": f"/media/products/{Path(row['image_file_path']).name}",
        "price": row["price"],
        "inventory": inventory,
        "total_stock": sum(item["quantity"] for item in inventory),
        "low_stock_sizes": _low_stock_sizes(inventory),
    }


def fetch_all_products() -> list[dict]:
    conn = get_connection()
    try:
        catalogue_rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        inventory_rows = conn.execute("SELECT product_id, size, quantity FROM inventory").fetchall()
    finally:
        conn.close()

    inventory_by_product: dict[str, list[dict]] = {}
    for inv in inventory_rows:
        inventory_by_product.setdefault(inv["product_id"], []).append(
            {"size": inv["size"], "quantity": inv["quantity"]}
        )

    return [
        serialize_product(row, inventory_by_product.get(row["product_id"], []))
        for row in catalogue_rows
    ]


def fetch_product(product_id: str) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            return None
        inventory = [
            {"size": inv["size"], "quantity": inv["quantity"]}
            for inv in conn.execute(
                "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
            ).fetchall()
        ]
    finally:
        conn.close()

    return serialize_product(row, inventory)


def fetch_user_by_id(user_id: int) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, name, email, first_name, last_name FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()
    return dict(row) if row else None


def fetch_chat_history(user_id: int, limit: int | None = None) -> list[dict]:
    """Chat history for one user, oldest first.

    limit=None returns the full history (for reloading the widget's visible
    log); a small limit returns only the most recent turns (for feeding the
    agent conversational context without letting the prompt grow unbounded).
    """
    conn = get_connection()
    try:
        query = "SELECT role, content, products_json, created_at FROM chat_messages WHERE user_id = ? ORDER BY id DESC"
        params: tuple = (user_id,)
        if limit is not None:
            query += " LIMIT ?"
            params = (user_id, limit)
        rows = conn.execute(query, params).fetchall()
    finally:
        conn.close()

    history = [
        {
            "role": row["role"],
            "content": row["content"],
            "products": json.loads(row["products_json"]) if row["products_json"] else [],
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    history.reverse()
    return history


def save_chat_message(user_id: int, role: str, content: str, products: list[dict] | None = None) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)",
            (user_id, role, content, json.dumps(products) if products else None),
        )
        conn.commit()
    finally:
        conn.close()
