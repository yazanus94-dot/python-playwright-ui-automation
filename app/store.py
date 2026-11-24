"""ShopEase demo storefront — FastAPI + Jinja2 + SQLite.

The system under test is a real, stateful application. Users, carts and orders
are persisted in SQLite; an opaque, HMAC-signed session cookie keys each
browser context to its own server-side state. Independent browser contexts and
pytest-xdist workers therefore cannot read or modify each other's state.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import sqlite3
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

MAX_QUANTITY = 10
COOKIE_NAME = "shopease_session"
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-for-local-testing-only")

PRODUCTS: list[dict[str, Any]] = [
    {
        "id": 1,
        "name": "Wireless Bluetooth Headphones",
        "category": "Electronics",
        "price": 79.99,
        "description": "Premium over-ear wireless headphones with noise cancellation.",
        "stock": 50,
        "rating": 4.7,
        "reviews": 128,
        "image": "/static/images/headphones.jpg",
    },
    {
        "id": 2,
        "name": "Protective Phone Case",
        "category": "Accessories",
        "price": 24.99,
        "description": "Shock-absorbent protective case with raised edges.",
        "stock": 120,
        "rating": 4.5,
        "reviews": 245,
        "image": "/static/images/case.jpg",
    },
    {
        "id": 3,
        "name": "Stainless Steel Water Bottle",
        "category": "Home & Kitchen",
        "price": 32.50,
        "description": "Insulated bottle, cold 24 hours or hot 12 hours.",
        "stock": 85,
        "rating": 4.8,
        "reviews": 312,
        "image": "/static/images/bottle.jpg",
    },
    {
        "id": 4,
        "name": "Mechanical Keyboard",
        "category": "Electronics",
        "price": 119.99,
        "description": "Compact mechanical keyboard with blue switches and RGB.",
        "stock": 35,
        "rating": 4.9,
        "reviews": 189,
        "image": "/static/images/keyboard.jpg",
    },
    {
        "id": 5,
        "name": "Running Shoes Air Cushion",
        "category": "Sports",
        "price": 89.99,
        "description": "Lightweight running shoes with air-cushion soles.",
        "stock": 60,
        "rating": 4.6,
        "reviews": 203,
        "image": "/static/images/shoes.jpg",
    },
    {
        "id": 6,
        "name": "Webcam 1080p",
        "category": "Electronics",
        "price": 59.99,
        "description": "Full HD webcam with microphone and privacy shutter.",
        "stock": 45,
        "rating": 4.4,
        "reviews": 156,
        "image": "/static/images/webcam.jpg",
    },
    {
        "id": 7,
        "name": "Aluminum Laptop Stand",
        "category": "Home & Kitchen",
        "price": 45.00,
        "description": "Ergonomic adjustable laptop stand with ventilation.",
        "stock": 70,
        "rating": 4.6,
        "reviews": 178,
        "image": "/static/images/stand.jpg",
    },
    {
        "id": 8,
        "name": "Programmable Coffee Maker",
        "category": "Home & Kitchen",
        "price": 69.99,
        "description": "12-cup programmable coffee maker with auto-shutoff.",
        "stock": 25,
        "rating": 4.7,
        "reviews": 134,
        "image": "/static/images/coffee.jpg",
    },
    {
        "id": 9,
        "name": "Non-Slip Yoga Mat",
        "category": "Sports",
        "price": 29.99,
        "description": "Extra-thick yoga mat with alignment lines and strap.",
        "stock": 90,
        "rating": 4.5,
        "reviews": 267,
        "image": "/static/images/yoga.jpg",
    },
    {
        "id": 10,
        "name": "Smart Watch",
        "category": "Electronics",
        "price": 199.99,
        "description": "Smart watch with heart rate, GPS and 7-day battery.",
        "stock": 40,
        "rating": 4.8,
        "reviews": 192,
        "image": "/static/images/watch.jpg",
    },
]

# ---------------------------------------------------------------------------
# SQLite persistence — one database file per server process (port), so xdist
# workers never contend. State is keyed by an opaque session id cookie.
# ---------------------------------------------------------------------------
PORT = int(os.environ.get("PORT", "5000"))
DB_PATH = Path(
    os.environ.get(
        "SHOP_EASE_DB",
        str(Path(tempfile.gettempdir()) / f"shopease_{PORT}.sqlite3"),
    )
)
DB_LOCK = threading.Lock()


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "email TEXT PRIMARY KEY, name TEXT NOT NULL, password TEXT NOT NULL)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS cart_items ("
            "sid TEXT NOT NULL, product_id INTEGER NOT NULL, quantity INTEGER NOT NULL, "
            "PRIMARY KEY (sid, product_id))"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS orders ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, sid TEXT NOT NULL, "
            "order_id TEXT UNIQUE NOT NULL, total REAL NOT NULL, status TEXT NOT NULL, "
            "created_at TEXT NOT NULL, customer_json TEXT NOT NULL, items_json TEXT NOT NULL)"
        )
        conn.execute(
            "INSERT OR IGNORE INTO users (email, name, password) VALUES (?, ?, ?)",
            ("demo@example.com", "Demo User", "DemoPass123!"),
        )
        conn.commit()


init_db()


# ---------------------------------------------------------------------------
# Signed cookie sessions (stdlib HMAC — no third-party session dependency).
# ---------------------------------------------------------------------------
def _sign(payload: dict[str, str]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(raw).decode().rstrip("=")
    mac = hmac.new(SECRET_KEY.encode(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{mac}"


def _unsign(token: str | None) -> dict[str, str] | None:
    if not token or "." not in token:
        return None
    body, mac = token.rsplit(".", 1)
    expected = hmac.new(SECRET_KEY.encode(), body.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(mac, expected):
        return None
    try:
        raw = base64.urlsafe_b64decode(body + "=" * (-len(body) % 4))
        payload = json.loads(raw)
        return (
            payload if isinstance(payload, dict) and isinstance(payload.get("sid"), str) else None
        )
    except (ValueError, TypeError):
        return None


def _session(request: Request) -> dict[str, str]:
    session = getattr(request.state, "session", None)
    if session is None:
        session = _unsign(request.cookies.get(COOKIE_NAME)) or {"sid": uuid.uuid4().hex}
    return session


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def get_product(product_id: int) -> dict[str, Any] | None:
    return next((p for p in PRODUCTS if p["id"] == product_id), None)


def _cart_rows(sid: str) -> dict[int, int]:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT product_id, quantity FROM cart_items WHERE sid = ?", (sid,)
        ).fetchall()
    return {int(product_id): int(quantity) for product_id, quantity in rows}


def cart_items(sid: str) -> tuple[list[dict[str, Any]], float]:
    items: list[dict[str, Any]] = []
    total = 0.0
    for product_id, quantity in sorted(_cart_rows(sid).items()):
        product = get_product(product_id)
        if product:
            subtotal = round(product["price"] * quantity, 2)
            items.append({**product, "quantity": quantity, "subtotal": subtotal})
            total += subtotal
    return items, round(total, 2)


def cart_count(sid: str) -> int:
    return sum(_cart_rows(sid).values())


def _orders(sid: str) -> list[dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT order_id, total, status, created_at, customer_json, items_json "
            "FROM orders WHERE sid = ? ORDER BY id DESC",
            (sid,),
        ).fetchall()
    return [
        {
            "order_id": row[0],
            "total": row[1],
            "status": row[2],
            "created_at": row[3],
            "customer": json.loads(row[4]),
            "items": json.loads(row[5]),
        }
        for row in rows
    ]


def parse_product_id(raw: Any) -> int | None:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def parse_quantity(raw: Any) -> int | None:
    try:
        quantity = int(raw)
    except (TypeError, ValueError):
        return None
    if quantity < 1 or quantity > MAX_QUANTITY:
        return None
    return quantity


async def _payload(request: Request) -> dict[str, Any]:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            data = await request.json()
            return data if isinstance(data, dict) else {}
        except ValueError:
            return {}
    form = await request.form()
    return dict(form)


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="ShopEase", docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.middleware("http")
async def session_middleware(request: Request, call_next):
    request.state.session = _session(request)
    response = await call_next(request)
    # Always re-set the signed cookie so login/user_email mutations persist.
    response.set_cookie(
        COOKIE_NAME,
        _sign(request.state.session),
        httponly=True,
        samesite="lax",
        path="/",
    )
    return response


def _render(
    request: Request,
    name: str,
    extra: dict[str, Any] | None = None,
    status_code: int = 200,
    **context: Any,
) -> HTMLResponse:
    """Render a template across Starlette's old and new TemplateResponse APIs."""
    ctx = dict(extra or {})
    ctx.setdefault("request", request)
    ctx.setdefault("session", _session(request))
    ctx.setdefault("url_for", _ctx(request)["url_for"])
    ctx.update(context)
    try:
        return templates.TemplateResponse(request, name, ctx, status_code=status_code)  # type: ignore
    except TypeError:
        return templates.TemplateResponse(name, ctx, status_code=status_code)  # type: ignore


def _ctx(request: Request, **extra: Any) -> dict[str, Any]:
    session = _session(request)
    ctx: dict[str, Any] = {"request": request, "session": session}

    def url_for(name: str, **params: Any) -> str:
        """Flask-style url_for for template compatibility."""
        if name == "static":
            return f"/static/{params.get('filename', '')}"
        return str(request.url_for(name, **params))

    ctx["url_for"] = url_for
    ctx.update(extra)
    return ctx


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "shopease"})


@app.get("/")
async def index(request: Request, q: str = "", category: str = "") -> HTMLResponse:
    products = [
        p for p in PRODUCTS if not category or p["category"].casefold() == category.casefold()
    ]
    if q:
        needle = q.casefold()
        products = [
            p
            for p in products
            if needle in p["name"].casefold() or needle in p["category"].casefold()
        ]
    sid = _session(request)["sid"]
    return _render(
        request,
        "index.html",
        _ctx(
            request,
            products=products,
            categories=sorted({p["category"] for p in PRODUCTS}),
            cart_count=cart_count(sid),
            query=q,
            selected_category=category,
        ),
    )


@app.get("/product/{product_id}")
async def product_detail(product_id: int, request: Request) -> HTMLResponse:
    product = get_product(product_id)
    sid = _session(request)["sid"]
    if product is None:
        return _render(
            request, "404.html", _ctx(request, cart_count=cart_count(sid)), status_code=404
        )
    return _render(
        request,
        "product.html",
        _ctx(request, product=product, cart_count=cart_count(sid), max_quantity=MAX_QUANTITY),
    )


@app.get("/cart")
async def cart_page(request: Request) -> HTMLResponse:
    sid = _session(request)["sid"]
    items, total = cart_items(sid)
    return _render(
        request,
        "cart.html",
        _ctx(request, cart_items=items, total=total, cart_count=cart_count(sid)),
    )


@app.post("/cart/add")
async def cart_add(request: Request) -> JSONResponse:
    payload = await _payload(request)
    product_id = parse_product_id(payload.get("product_id"))
    if product_id is None:
        return JSONResponse({"error": "Invalid product"}, status_code=400)
    quantity = parse_quantity(payload.get("quantity", 1))
    if get_product(product_id) is None:
        return JSONResponse({"error": "Product not found"}, status_code=404)
    if quantity is None:
        return JSONResponse(
            {"error": f"Quantity must be between 1 and {MAX_QUANTITY}"}, status_code=400
        )
    sid = _session(request)["sid"]
    with DB_LOCK, sqlite3.connect(DB_PATH) as conn:
        current = conn.execute(
            "SELECT quantity FROM cart_items WHERE sid = ? AND product_id = ?", (sid, product_id)
        ).fetchone()
        new_quantity = (int(current[0]) if current else 0) + quantity
        if new_quantity > MAX_QUANTITY:
            return JSONResponse({"error": f"Maximum quantity is {MAX_QUANTITY}"}, status_code=400)
        conn.execute(
            "INSERT INTO cart_items (sid, product_id, quantity) VALUES (?, ?, ?) "
            "ON CONFLICT(sid, product_id) DO UPDATE SET quantity = excluded.quantity",
            (sid, product_id, new_quantity),
        )
        conn.commit()
    return JSONResponse({"success": True, "cart_count": cart_count(sid)})


@app.post("/cart/update")
async def cart_update(request: Request) -> JSONResponse:
    payload = await _payload(request)
    quantity = parse_quantity(payload.get("quantity", 1))
    if quantity is None:
        return JSONResponse(
            {"error": f"Quantity must be between 1 and {MAX_QUANTITY}"}, status_code=400
        )
    product_id = parse_product_id(payload.get("product_id"))
    if product_id is None:
        return JSONResponse({"error": "Product not found"}, status_code=404)
    sid = _session(request)["sid"]
    with DB_LOCK, sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "UPDATE cart_items SET quantity = ? WHERE sid = ? AND product_id = ?",
            (quantity, sid, product_id),
        )
        if cursor.rowcount == 0:
            return JSONResponse({"error": "Product not in cart"}, status_code=404)
        conn.commit()
    return JSONResponse({"success": True, "cart_count": cart_count(sid)})


@app.post("/cart/remove")
async def cart_remove(request: Request) -> JSONResponse:
    payload = await _payload(request)
    raw = payload.get("product_id")
    sid = _session(request)["sid"]
    product_id = parse_product_id(raw)
    if product_id is None:
        product_id = -1
    with DB_LOCK, sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM cart_items WHERE sid = ? AND product_id = ?", (sid, product_id))
        conn.commit()
    return JSONResponse({"success": True, "cart_count": cart_count(sid)})


@app.get("/checkout")
async def checkout_page(request: Request):
    sid = _session(request)["sid"]
    items, total = cart_items(sid)
    if not items:
        return RedirectResponse("/", status_code=303)
    return _render(
        request,
        "checkout.html",
        _ctx(request, cart_items=items, total=total, cart_count=cart_count(sid)),
    )


@app.post("/checkout")
async def checkout_submit(request: Request) -> Response:
    sid = _session(request)["sid"]
    items, total = cart_items(sid)
    form = await request.form()
    name = str(form.get("customer_name", "")).strip()
    email = str(form.get("customer_email", "")).strip()
    address = str(form.get("customer_address", "")).strip()
    if not items:
        return RedirectResponse("/", status_code=303)
    if not name or "@" not in email or not address:
        return _render(
            request,
            "checkout.html",
            _ctx(
                request,
                cart_items=items,
                total=total,
                cart_count=cart_count(sid),
                error="Please complete all fields.",
            ),
        )
    order = {
        "order_id": uuid.uuid4().hex[:8].upper(),
        "items": items,
        "total": total,
        "status": "confirmed",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "customer": {"name": name, "email": email, "address": address},
    }
    with DB_LOCK, sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO orders (sid, order_id, total, status, created_at, customer_json, items_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                sid,
                order["order_id"],
                total,
                "confirmed",
                order["created_at"],
                json.dumps(order["customer"]),
                json.dumps(order["items"]),
            ),
        )
        conn.execute("DELETE FROM cart_items WHERE sid = ?", (sid,))
        conn.commit()
    _session(request)["user_email"] = email
    return _render(request, "order_confirmation.html", _ctx(request, order=order, cart_count=0))


@app.get("/orders")
async def order_history(request: Request):
    session = _session(request)
    if "user_email" not in session:
        return RedirectResponse("/login", status_code=303)
    return _render(request, "order_history.html", _ctx(request, orders=_orders(session["sid"])))


@app.get("/orders/{order_id}")
async def order_detail(order_id: str, request: Request) -> HTMLResponse:
    sid = _session(request)["sid"]
    order = next((o for o in _orders(sid) if o["order_id"] == order_id), None)
    if order is None:
        return _render(
            request, "404.html", _ctx(request, cart_count=cart_count(sid)), status_code=404
        )
    return _render(request, "order_detail.html", _ctx(request, order=order))


@app.get("/login")
async def login_page(request: Request) -> HTMLResponse:
    return _render(request, "login.html", _ctx(request))


@app.post("/login")
async def login_submit(request: Request):
    form = await request.form()
    email = str(form.get("email", "")).strip()
    password = str(form.get("password", ""))
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT password FROM users WHERE email = ?", (email,)).fetchone()
    if row and row[0] == password:
        _session(request)["user_email"] = email
        return RedirectResponse("/", status_code=303)
    return _render(request, "login.html", _ctx(request, error="Invalid credentials"))


@app.get("/register")
async def register_page(request: Request) -> HTMLResponse:
    return _render(request, "register.html", _ctx(request))


@app.post("/register")
async def register_submit(request: Request):
    form = await request.form()
    name = str(form.get("name", "")).strip()
    email = str(form.get("email", "")).strip()
    password = str(form.get("password", ""))
    if not name or "@" not in email or len(password) < 8:
        return _render(request, "register.html", _ctx(request, error="Invalid registration data"))
    with DB_LOCK, sqlite3.connect(DB_PATH) as conn:
        if conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
            return _render(
                request, "register.html", _ctx(request, error="Email already registered")
            )
        conn.execute(
            "INSERT INTO users (email, name, password) VALUES (?, ?, ?)", (email, name, password)
        )
        conn.commit()
    _session(request)["user_email"] = email
    return RedirectResponse("/", status_code=303)


@app.get("/logout")
async def logout(request: Request) -> RedirectResponse:
    _session(request).pop("user_email", None)
    return RedirectResponse("/", status_code=303)


@app.get("/api/products")
async def api_products() -> JSONResponse:
    return JSONResponse(PRODUCTS)


@app.get("/api/products/{product_id}")
async def api_product(product_id: int) -> JSONResponse:
    product = get_product(product_id)
    if product is None:
        return JSONResponse({"error": "Not found"}, status_code=404)
    return JSONResponse(product)


# Backwards-compatible alias used by app.main.
application = app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")
