"""Campus Customs API.

Run from backend/:  uvicorn main:app --reload --port 8000
Open API docs:      http://127.0.0.1:8000/docs
Frontend (Vite):    http://127.0.0.1:5173
"""

import sqlite3

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field, field_validator

from agent import ChatDeps, run_agent
from db import (
    BASE_DIR,
    PRODUCTS_DIR,
    fetch_all_products,
    fetch_chat_history,
    fetch_product,
    fetch_user_by_id,
    get_connection,
    save_chat_message,
)
from models import ChatHistoryMessage, ChatReply, CustomerContext
from security import hash_password, verify_password

MAX_HISTORY_MESSAGES_FOR_AGENT = 12  # ~6 turns of conversational memory per request

load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")

app = FastAPI(title="Campus Customs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media/products", StaticFiles(directory=PRODUCTS_DIR), name="product-images")


@app.get("/api/products")
def list_products():
    return fetch_all_products()


@app.get("/api/products/{product_id}")
def get_product(product_id: str):
    product = fetch_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    confirm_password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    first_name: str | None
    last_name: str | None
    name: str
    email: str


def serialize_user(row: sqlite3.Row) -> UserOut:
    return UserOut(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        name=row["name"],
        email=row["email"],
    )


@app.post("/api/auth/register", response_model=UserOut, status_code=201)
def register(payload: RegisterRequest):
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?", (payload.email.lower(),)
        ).fetchone()
        if existing is not None:
            raise HTTPException(status_code=409, detail="An account with that email already exists")

        full_name = f"{payload.first_name} {payload.last_name}".strip()
        password_hash = hash_password(payload.password)
        cursor = conn.execute(
            """
            INSERT INTO users (name, email, password_hash, first_name, last_name)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name, payload.email.lower(), password_hash, payload.first_name, payload.last_name),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
    finally:
        conn.close()

    return serialize_user(row)


@app.post("/api/auth/login", response_model=UserOut)
def login(payload: LoginRequest):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (payload.email.lower(),)
        ).fetchone()
    finally:
        conn.close()

    if row is None or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return serialize_user(row)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    user_id: int | None = Field(
        default=None, description="Logged-in user's id, or None for a guest."
    )
    current_product_id: str | None = Field(
        default=None, description="Catalogue id of the product page the customer is currently viewing, if any."
    )


@app.get("/api/chat/history", response_model=list[ChatHistoryMessage])
def chat_history(user_id: int):
    """Full chat history for a logged-in customer, for reloading the widget when they return."""
    return fetch_chat_history(user_id)


@app.post("/api/chat", response_model=ChatReply)
def chat(payload: ChatRequest):
    customer: CustomerContext | None = None
    history: list[dict] | None = None

    if payload.user_id is not None:
        user_row = fetch_user_by_id(payload.user_id)
        if user_row is not None:
            customer = CustomerContext(id=user_row["id"], name=user_row["name"], email=user_row["email"])
            history = fetch_chat_history(customer.id, limit=MAX_HISTORY_MESSAGES_FOR_AGENT)

    deps = ChatDeps(customer=customer, current_product_id=payload.current_product_id)
    reply = run_agent(payload.message, deps=deps, history=history)

    if customer is not None:
        save_chat_message(customer.id, "user", payload.message)
        save_chat_message(
            customer.id,
            "assistant",
            reply.reply,
            [p.model_dump() for p in reply.products] or None,
        )

    return reply


@app.get("/api/health")
def health():
    return {"status": "ok"}
