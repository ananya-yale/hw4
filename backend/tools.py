"""Agent tools for looking up Campus Customs products.

All three tools read straight from the catalogue/inventory tables (db.py) —
the same source of truth the /api/products routes use — so the agent never
guesses at a product, price, or stock level; it always calls a tool.

search_products does a simple keyword/tag overlap search rather than a
second LLM call to rank results: the catalogue is small (~100 items) and
each product already carries curated search_tags, so plain token matching
against name/description/garment_type/colors/search_tags is enough to find
genuinely relevant items without the extra cost and latency of another
model round trip. It's also typo-tolerant (difflib fuzzy matching as a
fallback for words with no exact hit) — all done in Python, so a misspelled
query ("hoody", "crewnek") still costs zero extra model calls/tokens.

check_size_stock computes its own in_stock flag and ready-to-say message in
Python rather than returning raw numbers for the model to interpret — this
is what actually guarantees "never invent stock" and "say sold out clearly"
instead of just hoping the model reads the inventory list correctly. It also
flags low stock (<= LOW_STOCK_THRESHOLD units) so the agent can mention
genuine urgency without ever rounding or guessing a number.
"""

import difflib
from typing import List, Optional

from db import LOW_STOCK_THRESHOLD, fetch_all_products, fetch_product
from models import ProductCard, StockCheck

MAX_RESULTS = 8
FUZZY_MATCH_CUTOFF = 0.7  # catches typos like "hoody"->"hoodie", "crewnek"->"crewneck"
FUZZY_MIN_WORD_LENGTH = 4  # skip short words to avoid spurious fuzzy hits


def _product_text(product: dict) -> str:
    parts = [
        product["name"],
        product["garment_type"],
        product["description"],
        " ".join(product["colors"]),
        " ".join(product["search_tags"]),
    ]
    return " ".join(parts).lower()


def _to_card(product: dict) -> ProductCard:
    return ProductCard(**product)


def _word_score(word: str, text: str, tokens: set[str]) -> float:
    """1.0 for an exact substring hit, 0.6 for a close-enough fuzzy match, else 0."""
    if word in text:
        return 1.0
    if len(word) >= FUZZY_MIN_WORD_LENGTH:
        if difflib.get_close_matches(word, tokens, n=1, cutoff=FUZZY_MATCH_CUTOFF):
            return 0.6
    return 0.0


def search_products(query: str, limit: int = MAX_RESULTS) -> List[ProductCard]:
    """Search the Campus Customs catalogue by keyword or topic.

    Matches the query's words against each product's name, description,
    garment type, colors, and search tags, and returns the best matches
    ranked by how many query words they hit. Tolerates minor typos (e.g.
    "hoody", "crewnek") via fuzzy matching, so a misspelling doesn't return
    zero results.

    Args:
        query: What the customer is looking for, e.g. "navy hoodie" or
            "yale hockey gear".
        limit: Maximum number of products to return (capped at 8).
    """
    limit = max(1, min(limit, MAX_RESULTS))
    words = [w for w in query.lower().split() if w]
    if not words:
        return []

    scored = []
    for product in fetch_all_products():
        text = _product_text(product)
        tokens = set(text.split())
        score = sum(_word_score(word, text, tokens) for word in words)
        if score > 0:
            scored.append((score, product))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [_to_card(product) for _, product in scored[:limit]]


def get_product_details(product_id: str) -> Optional[ProductCard]:
    """Look up full details (description, price, colors, sizes/stock) for one product.

    Args:
        product_id: The catalogue id of the product, e.g. 'basic-hoodie-big-yale'.
            Get this from a prior search_products call.
    """
    product = fetch_product(product_id)
    return _to_card(product) if product else None


def check_size_stock(product_id: str, size: str) -> StockCheck:
    """Check whether one specific size of a product is in stock, and how many.

    Always use this (not get_product_details' inventory list) when a customer
    asks about a specific size — it returns an already-correct in_stock flag
    and message, so you just relay it rather than reading the raw numbers
    yourself.

    Args:
        product_id: The catalogue id of the product, e.g. 'basic-hoodie-big-yale'.
        size: The size to check, e.g. 'S', 'M', 'L', 'XL'.
    """
    product = fetch_product(product_id)
    if product is None:
        return StockCheck(
            product_id=product_id,
            size=size,
            found=False,
            quantity=0,
            in_stock=False,
            low_stock=False,
            message=f"No product found with id '{product_id}'.",
        )

    normalized = size.strip().upper()
    match = next((item for item in product["inventory"] if item["size"].upper() == normalized), None)
    if match is None:
        available = ", ".join(item["size"] for item in product["inventory"])
        return StockCheck(
            product_id=product_id,
            size=size,
            found=False,
            quantity=0,
            in_stock=False,
            low_stock=False,
            message=f"'{size}' isn't a size we carry for {product['name']}. Available sizes: {available}.",
        )

    quantity = match["quantity"]
    in_stock = quantity > 0
    low_stock = in_stock and quantity <= LOW_STOCK_THRESHOLD
    if not in_stock:
        message = f"{product['name']} in size {match['size']} is sold out."
    elif low_stock:
        message = f"{product['name']} in size {match['size']}: only {quantity} left!"
    else:
        message = f"{product['name']} in size {match['size']}: {quantity} in stock."
    return StockCheck(
        product_id=product_id,
        size=match["size"],
        found=True,
        quantity=quantity,
        in_stock=in_stock,
        low_stock=low_stock,
        message=message,
    )
