# Architecture

## Components

| Layer | Implementation | Responsibility |
|---|---|---|
| System under test | `app/store.py` (Flask) | Real catalogue, cart, checkout, orders, auth and health endpoint |
| Templates | `app/templates/*.html`, `app/static/` | UI with stable `data-testid` hooks and accessible markup |
| Configuration | `config/settings.py` | Env-driven base URL, timeout, browser, artifact paths |
| Fixtures | `tests/conftest.py` | SUT lifecycle, per-test context, evidence, page-object factories |
| Page Objects | `tests/pages/*.py` | Locator encapsulation and reusable customer actions |
| Tests | `tests/test_*.py` | Business behaviour and assertions only |
| Infrastructure | `Dockerfile`, `docker-compose.yml`, `.github/workflows/ui-tests.yml` | Reproducible local and CI execution |

## State model and isolation

`CARTS`, `ORDERS` and `USERS` are server-side dictionaries keyed by an opaque `sid`. The `sid` is
created on first request and stored in Flask's signed session cookie. Consequently:

- Each browser context owns its own cart and orders.
- Logging out or checking out in one context cannot affect another.
- pytest-xdist workers share a server (when `EXTERNAL_SUT_URL` is used) but never share state.

Resetting a Python application object inside a worker would not reset a separate server process;
the sid-keyed design fixes the scaffold defect at its root.

## SUT lifecycle

- Local: `live_server` starts `python app/store.py` on `5100 + worker_index` and polls `/health`.
- Docker/CI: `EXTERNAL_SUT_URL` is set; fixtures poll `/health` of the already-started service.
- Cleanup is in `finally` blocks, so a failing test cannot leak a process.

## Evidence pipeline

- Every test gets a fresh context with `record_video_dir`.
- Video handles are collected **before** `context.close()` (the page list is cleared on close).
- On a failed call phase, a full-page screenshot is captured and attached to the correct Allure
  result via the `pytest_runtest_makereport` hook.
- Artifact filenames include the full node ID, which makes parametrized cases unique.

## Browser selection

`BROWSER` sets `config.option.browser` as a list in `pytest_configure`, matching the
`pytest-playwright` CLI contract. Chromium, Firefox and WebKit are installed and exercised.

## Delivery

- Dockerfile: official Playwright Python image `v1.65.2-noble`, matching the pinned package.
- Compose: `storefront` (healthchecked) and `tests` services on a private network.
- CI: real browser tests in a three-browser matrix with minimal `contents: read` permission.
