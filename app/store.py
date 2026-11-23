"""ShopEase demo storefront — a real, stateful system under test.

All mutable customer state is stored server-side and keyed by an opaque session
identifier held in a signed cookie. Separate browser contexts therefore cannot
read or modify each other's carts or orders, including under pytest-xdist.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

MAX_QUANTITY = 10
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

# Server-side state keyed by opaque session id. No cross-context globals.
CARTS: dict[str, dict[str, int]] = {}
ORDERS: dict[str, list[dict[str, Any]]] = {}
USERS: dict[str, dict[str, str]] = {
    "demo@example.com": {
        "name": "Demo User",
        "email": "demo@example.com",
        "password": "DemoPass123!",
    },
}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-for-local-testing-only")


def current_session_id() -> str:
    sid = session.get("sid")
    if not sid:
        sid = uuid.uuid4().hex
        session["sid"] = sid
    return sid


def get_product(product_id: int) -> dict[str, Any] | None:
    return next((product for product in PRODUCTS if product["id"] == product_id), None)


def cart_items(sid: str) -> tuple[list[dict[str, Any]], float]:
    items: list[dict[str, Any]] = []
    total = 0.0
    for product_id, quantity in CARTS.get(sid, {}).items():
        product = get_product(int(product_id))
        if product:
            subtotal = round(product["price"] * quantity, 2)
            items.append({**product, "quantity": quantity, "subtotal": subtotal})
            total += subtotal
    return items, round(total, 2)


def cart_count(sid: str) -> int:
    return sum(CARTS.get(sid, {}).values())


def parse_quantity(raw: Any) -> int | None:
    try:
        quantity = int(raw)
    except (TypeError, ValueError):
        return None
    if quantity < 1 or quantity > MAX_QUANTITY:
        return None
    return quantity


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "shopease"})


@app.get("/")
def index():
    query = request.args.get("q", "")
    category = request.args.get("category", "")
    products = [
        p for p in PRODUCTS if not category or p["category"].casefold() == category.casefold()
    ]
    if query:
        needle = query.casefold()
        products = [
            p
            for p in products
            if needle in p["name"].casefold() or needle in p["category"].casefold()
        ]
    sid = current_session_id()
    return render_template(
        "index.html",
        products=products,
        categories=sorted({p["category"] for p in PRODUCTS}),
        cart_count=cart_count(sid),
        query=query,
        selected_category=category,
        session=session,
    )


@app.get("/product/<int:product_id>")
def product_detail(product_id: int):
    product = get_product(product_id)
    if product is None:
        return render_template("404.html"), 404
    sid = current_session_id()
    return render_template(
        "product.html",
        product=product,
        cart_count=cart_count(sid),
        max_quantity=MAX_QUANTITY,
        session=session,
    )


@app.get("/cart")
def cart_page():
    sid = current_session_id()
    items, total = cart_items(sid)
    return render_template(
        "cart.html", cart_items=items, total=total, cart_count=cart_count(sid), session=session
    )


@app.post("/cart/add")
def cart_add():
    payload = request.get_json(silent=True) or request.form
    try:
        product_id = int(payload.get("product_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid product"}), 400
    quantity = parse_quantity(payload.get("quantity", 1))
    if get_product(product_id) is None:
        return jsonify({"error": "Product not found"}), 404
    if quantity is None:
        return jsonify({"error": f"Quantity must be between 1 and {MAX_QUANTITY}"}), 400
    sid = current_session_id()
    cart = CARTS.setdefault(sid, {})
    key = str(product_id)
    new_quantity = cart.get(key, 0) + quantity
    if new_quantity > MAX_QUANTITY:
        return jsonify({"error": f"Maximum quantity is {MAX_QUANTITY}"}), 400
    cart[key] = new_quantity
    return jsonify({"success": True, "cart_count": cart_count(sid)})


@app.post("/cart/update")
def cart_update():
    payload = request.get_json(silent=True) or request.form
    quantity = parse_quantity(payload.get("quantity", 1))
    if quantity is None:
        return jsonify({"error": f"Quantity must be between 1 and {MAX_QUANTITY}"}), 400
    sid = current_session_id()
    cart = CARTS.setdefault(sid, {})
    key = str(payload.get("product_id"))
    if key not in cart:
        return jsonify({"error": "Product not in cart"}), 404
    cart[key] = quantity
    return jsonify({"success": True, "cart_count": cart_count(sid)})


@app.post("/cart/remove")
def cart_remove():
    sid = current_session_id()
    key = str(
        request.values.get("product_id") or (request.get_json(silent=True) or {}).get("product_id")
    )
    CARTS.setdefault(sid, {}).pop(key, None)
    return jsonify({"success": True, "cart_count": cart_count(sid)})


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    sid = current_session_id()
    items, total = cart_items(sid)
    if not items:
        return redirect(url_for("index"))
    if request.method == "POST":
        name = request.form.get("customer_name", "").strip()
        email = request.form.get("customer_email", "").strip()
        address = request.form.get("customer_address", "").strip()
        if not name or "@" not in email or not address:
            return render_template(
                "checkout.html",
                cart_items=items,
                total=total,
                cart_count=cart_count(sid),
                error="Please complete all fields.",
                session=session,
            )
        order = {
            "order_id": uuid.uuid4().hex[:8].upper(),
            "items": items,
            "total": total,
            "status": "confirmed",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "customer": {"name": name, "email": email, "address": address},
        }
        ORDERS.setdefault(sid, []).insert(0, order)
        CARTS[sid] = {}
        session["user_email"] = email
        return render_template(
            "order_confirmation.html", order=order, cart_count=0, session=session
        )
    return render_template(
        "checkout.html", cart_items=items, total=total, cart_count=cart_count(sid), session=session
    )


@app.get("/orders")
def order_history():
    sid = current_session_id()
    if "user_email" not in session:
        return redirect(url_for("login"))
    return render_template("order_history.html", orders=ORDERS.get(sid, []), session=session)


@app.get("/orders/<order_id>")
def order_detail(order_id: str):
    sid = current_session_id()
    order = next((o for o in ORDERS.get(sid, []) if o["order_id"] == order_id), None)
    if order is None:
        return render_template("404.html"), 404
    return render_template("order_detail.html", order=order, session=session)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = USERS.get(email)
        if user and user["password"] == password:
            session["user_email"] = email
            return redirect(url_for("index"))
        return render_template("login.html", error="Invalid credentials", session=session)
    return render_template("login.html", session=session)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if not name or "@" not in email or len(password) < 8:
            return render_template(
                "register.html", error="Invalid registration data", session=session
            )
        if email in USERS:
            return render_template(
                "register.html", error="Email already registered", session=session
            )
        USERS[email] = {"name": name, "email": email, "password": password}
        session["user_email"] = email
        return redirect(url_for("index"))
    return render_template("register.html", session=session)


@app.get("/logout")
def logout():
    session.pop("user_email", None)
    return redirect(url_for("index"))


@app.get("/api/products")
def api_products():
    return jsonify(PRODUCTS)


@app.get("/api/products/<int:product_id>")
def api_product(product_id: int):
    product = get_product(product_id)
    if product is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(product)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
