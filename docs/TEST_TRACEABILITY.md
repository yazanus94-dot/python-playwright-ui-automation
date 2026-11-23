# Test Traceability

## Requirement → coverage

| Requirement (directive phase) | Test case IDs | Collected cases | Result |
|---|---|---:|---|
| Catalogue, pricing, navigation (A/Phase C) | TC-HOME-001..005 | 5 | Passed |
| Search incl. case/no-result/empty (C) | TC-SEARCH-001..004 | 6 | Passed |
| Category filtering + combined filter (C) | TC-CAT-001..002 | 5 | Passed |
| All product details and invalid product (C) | TC-PROD-001..005 | 14 | Passed |
| Cart add/update/remove/subtotals/totals (C) | TC-CART-001..009 | 8+1 | Passed |
| Checkout, confirmation, cart clearing, history (A/C) | TC-CO-001..008 | 8 | Passed |
| Authentication and form validation (C) | TC-AUTH-001..008 | 8 | Passed |
| Negative/invalid requests (C) | TC-NEG-001..008 | 11 | Passed |
| Session isolation (A/C) | TC-ISO-001..004 | 4 | Passed |
| Cross-browser regression (D) | all of the above | 70 x 3 browsers | Passed |
| Parallel execution (D) | all of the above | 70 x 2 workers | Passed |

## Parametrization accounting

53 unique test functions produce 70 collected cases:

| Function | Parameter sets | Cases |
|---|---:|---:|
| `test_search_returns_matching_product` | 3 queries | 3 |
| `test_category_filter` | 4 categories | 4 |
| `test_product_details` | 10 products | 10 |
| `test_invalid_quantity_rejected` | 0, -1, 11, 999 | 4 |
| Other 49 functions | 1 each | 49 |
| **Total** | | **70** |

`pytest --collect-only -q` output: **70 tests collected**.

## Isolation evidence

- TC-ISO-001: context B cart count 0 while context A has a product.
- TC-ISO-002: context B cannot see context A's order ID.
- TC-ISO-003: context A checkout leaves context B's cart untouched.
- TC-ISO-004: two contexts checkout concurrently and receive distinct order IDs.
- `pytest -n 2 -v`: 70 passed; state is keyed by server-side sid, not worker-local objects.

## Execution evidence summary

| Run | Result |
|---|---|
| `pytest -m smoke -v` | 7 passed, 63 deselected |
| `pytest -m regression -v` | 70 passed |
| `pytest -n 2 -v` | 70 passed |
| `BROWSER=chromium pytest -v` | 70 passed |
| `BROWSER=firefox pytest -v` | 70 passed |
| `BROWSER=webkit pytest -v` | 70 passed |
| `docker compose run --rm tests` | 70 passed |
| Allure CLI 2.46.1 + Java 26.0.2.1 | `allure generate` exit 0 |
| Failure evidence probe | 1 PNG + 1 WEBM attached |
