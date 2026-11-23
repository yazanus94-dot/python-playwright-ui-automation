// ShopEase - Frontend JavaScript

document.addEventListener("DOMContentLoaded", () => {
    initAddToCart();
    initCartActions();
});

function initAddToCart() {
    const detailForm = document.getElementById("add-to-cart-form");

    document.querySelectorAll(".add-to-cart").forEach((button) => {
        button.addEventListener("click", (e) => {
            // The product page form has its own submit handler; do not double-add.
            if (detailForm && detailForm.contains(button)) return;
            e.preventDefault();
            const productId = button.dataset.id;
            const form = document.getElementById("add-to-cart-form");
            let quantity = 1;
            if (form) {
                const qtyInput = form.querySelector('input[name="quantity"]');
                if (qtyInput) quantity = parseInt(qtyInput.value, 10) || 1;
            }
            addToCart(productId, quantity);
        });
    });

    if (detailForm) {
        detailForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const productId = detailForm.dataset.id;
            const qtyInput = detailForm.querySelector('input[name="quantity"]');
            const quantity = qtyInput ? parseInt(qtyInput.value, 10) || 1 : 1;
            addToCart(productId, quantity);
        });
    }
}

async function addToCart(productId, quantity) {
    try {
        const response = await fetch("/cart/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ product_id: productId, quantity }),
        });
        const result = await response.json();
        if (result.success) {
            updateCartCount(result.cart_count);
            showToast("Added to cart");
        }
    } catch (error) {
        console.error("Add to cart failed:", error);
    }
}

function initCartActions() {
    document.querySelectorAll(".update-qty").forEach((button) => {
        button.addEventListener("click", async (e) => {
            e.preventDefault();
            const form = button.closest("form");
            if (!form) return;
            const itemId = form.dataset.id;
            const input = form.querySelector('input[name="quantity"]');
            const quantity = input ? parseInt(input.value, 10) || 1 : 1;
            await updateCartItem(itemId, quantity);
        });
    });

    document.querySelectorAll(".remove-item").forEach((button) => {
        button.addEventListener("click", async (e) => {
            e.preventDefault();
            await removeCartItem(button.dataset.id);
        });
    });
}

async function updateCartItem(productId, quantity) {
    try {
        const response = await fetch("/cart/update", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ product_id: productId, quantity }),
        });
        const result = await response.json();
        if (result.success) {
            updateCartCount(result.cart_count);
            location.reload();
        }
    } catch (error) {
        console.error("Update cart failed:", error);
    }
}

async function removeCartItem(productId) {
    if (!confirm("Remove this item from cart?")) return;
    try {
        const response = await fetch("/cart/remove", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ product_id: productId }),
        });
        const result = await response.json();
        if (result.success) {
            updateCartCount(result.cart_count);
            location.reload();
        }
    } catch (error) {
        console.error("Remove from cart failed:", error);
    }
}

function updateCartCount(count) {
    document.querySelectorAll("#cart-count").forEach((el) => {
        el.textContent = count;
    });
}

function showToast(message) {
    const toast = document.createElement("div");
    toast.style.cssText =
        "position:fixed;top:20px;right:20px;background:#059669;color:white;" +
        "padding:1rem 1.5rem;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,.15);" +
        "z-index:1000;font-size:.95rem;";
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}
