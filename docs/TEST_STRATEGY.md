# Test Strategy

## Objectives

Verify the storefront as a real user would: catalogue browsing, search, category filtering, product
details, cart maths, checkout, order history, authentication and invalid-input handling. Assertions
focus on observable outcomes (visible elements, computed totals, redirected URLs, HTTP status).

## Test levels and markers

| Marker | Meaning | Collected cases |
|---|---|---|
| `smoke` | Critical paths | 7 |
| `regression` | Full functional coverage (all current cases) | 70 |
| `negative` | Invalid requests, quantities, products and methods | 11 |
| `isolation` | Independent browser contexts | 4 |

## Coverage matrix

| Area | Cases |
|---|---|
| Homepage and catalogue | 17 |
| Product details | 14 |
| Negative scenarios | 11 |
| Cart | 8 |
| Authentication | 8 |
| Checkout and orders | 8 |
| Session isolation | 4 |

## Design rules

- One Page Object per UI area; tests contain no raw locators.
- Accessible locators (`get_by_role`, labels, test IDs) only.
- Playwright auto-waiting and web-first assertions; no `time.sleep()` in tests.
- Form submissions use explicit navigation waits; async cart updates wait for the cart count.
- Parametrization is used only for genuinely different inputs/outcomes (10 products, 4 categories,
  4 invalid quantities, 4 searches).

## Defects found and fixed during execution

1. Product page had no `app.js` include — add-to-cart was inert. Script added to all templates.
2. Double add-to-cart handler on the submit button — click handler now defers to the form handler.
3. `order_confirmation.html` had systematic `c`→`l` corruption — template rewritten.
4. `order.items` resolved to the dict method in Jinja — changed to `order["items"]`.
5. Checkout address was a textarea but the page object targeted an input — fixed.
6. Checkout validation error was never rendered — added `novalidate` plus error block.
7. Port 5000 was occupied locally — per-worker ports start at 5100.
8. WebKit navigation races — explicit navigation waits and cart-count waits added.
9. Videos were attached after context close when the page list was empty — handles captured first.

No assertion was weakened and no failing test was skipped to reach a green result.

## Execution evidence

| Command | Result |
|---|---|
| `pytest --collect-only -q` | 70 collected |
| `pytest -m smoke -v` | 7 passed, 63 deselected |
| `pytest -m regression -v` | 70 passed |
| `pytest -n 2 -v` | 70 passed |
| Chromium / Firefox / WebKit full suites | 70 passed each |
| `docker compose run --rm tests` | 70 passed |

## Known risks

- Python 3.12 is unavailable locally; CI runs 3.12.
- Third-party `pytest-asyncio` emits deprecation warnings under Python 3.14.
- Failure screenshots are absent in a fully green final run by design; capture was proven with a
  temporary failing probe (1 PNG + 1 WEBM Allure attachment).
