"""
Pydantic types shared by the Campus Customs agent (agent.py, tools.py) and
exposed through the chat API (main.py).

ProductCard mirrors the shape already served by GET /api/products (see
serialize_product in main.py) so the same data the catalogue/inventory
tables produce for the shop pages can also be attached to a chat reply and
rendered by the same ProductCard component on the frontend.
"""

from typing import List

from pydantic import BaseModel, Field


class SizeStock(BaseModel):
    size: str = Field(..., description="Size label, e.g. 'S', 'M', 'XL'.")
    quantity: int = Field(..., description="Units currently in stock for this size.")


class ProductCard(BaseModel):
    """A single product, with enough detail to render a card in the chat UI."""

    product_id: str = Field(..., description="Catalogue id, e.g. 'basic-hoodie-big-yale'.")
    name: str = Field(..., description="Product display name.")
    garment_type: str = Field(..., description="Category of item, e.g. 'pullover hoodie'.")
    description: str = Field(..., description="Short description of the product.")
    colors: List[str] = Field(default_factory=list, description="Colors this product comes in.")
    image_url: str = Field(..., description="Path to the product image, served by this API.")
    price: float = Field(..., description="Price in USD.")
    inventory: List[SizeStock] = Field(default_factory=list, description="Stock by size.")
    total_stock: int = Field(..., description="Total units in stock across all sizes.")
    low_stock_sizes: List[str] = Field(
        default_factory=list,
        description="Sizes that are in stock but low (a few units left) — ok to mention for gentle urgency.",
    )


class StockCheck(BaseModel):
    """Result of checking stock for one product/size combination.

    `in_stock` and `message` are computed in Python (tools.py), not left for
    the model to infer from raw numbers — so "sold out" vs "N in stock" is
    always phrased correctly and the agent only has to relay it, never
    calculate or reinterpret it.
    """

    product_id: str = Field(..., description="Catalogue id that was checked.")
    size: str = Field(..., description="The size that was checked (as matched in our inventory, e.g. 'M').")
    found: bool = Field(..., description="Whether this product_id/size combination exists at all.")
    quantity: int = Field(..., description="Units in stock for this size. 0 if sold out or not found.")
    in_stock: bool = Field(..., description="True if quantity > 0.")
    low_stock: bool = Field(..., description="True if in stock but at or below the low-stock threshold.")
    message: str = Field(
        ...,
        description=(
            "Ready-to-relay, correctly-phrased stock status, e.g. 'Sold out in size M.' or "
            "'Only 2 left!' when low_stock is true."
        ),
    )


class ChatReply(BaseModel):
    """The agent's structured output for one turn of the shop chatbot.

    `reply` is always shown as the assistant's message text. `products` is
    optional — populated only when the agent found specific items worth
    showing (e.g. after a search_products or get_product_details tool
    call), so the frontend can render product cards alongside the text.
    """

    reply: str = Field(..., description="The assistant's natural-language response to the customer.")
    products: List[ProductCard] = Field(
        default_factory=list,
        description="Products to display as cards alongside the reply, if any are relevant. Empty if none.",
    )


class CustomerContext(BaseModel):
    """Who the agent is chatting with, for a logged-in customer.

    Deliberately minimal: just enough for the agent to personalize a reply
    (e.g. use a first name) and to key chat history lookups/saves by. Never
    includes password_hash or anything else sensitive from the users table.
    """

    id: int = Field(..., description="users.id — used to load/save this customer's chat history.")
    name: str = Field(..., description="Customer's full display name.")
    email: str = Field(..., description="Customer's account email.")


class ChatHistoryMessage(BaseModel):
    """One persisted turn of a logged-in customer's chat history (chat_messages table)."""

    role: str = Field(..., description="'user' or 'assistant'.")
    content: str = Field(..., description="The message text.")
    products: List[ProductCard] = Field(
        default_factory=list, description="Product cards attached to this turn, if any."
    )
    created_at: str = Field(..., description="When this message was stored.")
