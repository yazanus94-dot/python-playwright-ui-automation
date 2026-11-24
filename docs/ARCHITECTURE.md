# Architecture

## Components

| Layer | Implementation | Responsibility |
|---|---|---|
| System under test | `app/store.py` (FastAPI) | Real catalogue, cart, checkout, orders, auth and health endpoint |
| Persistence | SQLite (`users`, `cart_items`, `orders`) | Durable users, carts and orders keyed by opaque session id |
| Templates | `app/templates/*.html`, `app/static/` via Jinja2 | UI with stable `data-testid` hooks and accessible markup |
| Configuration | `config/settings.py` | Env-driven base URL, timeout, browser, artifact paths |
| Fixtures | `tests/conftest.py` | SUT lifecycle, per-test context, evidence, page-object factories |
| Page Objects | `tests/pages/*.py` | Locator encapsulation and reusable customer actions |
| Tests | `tests/test_*.py` | Business behaviour and assertions only |
| Infrastructure | `Dockerfile`, `docker-compose.yml`, `.github/workflows/ui-tests.yml` | Reproducible local and CI execution |

## State model and isolation

`users`, `cart_items` and `orders` are SQLite tables keyed by an opaque `sid`. The `sid` and the
logged-in `user_email` travel in an HMAC-signed, HTTP-only cookie created by stdlib `hmac`. Every
request carries its own cookie, so:

- Each browser context owns its own cart and orders in SQLite.
- Logging out or checking out in one context cannot affect another.
- pytest-xdist workers never share state: local runs use a separate SQLite database per worker
  (`shopease_<port>.sqlite3` in the system temp dir), and the fixture removes it at session start
  so repeated runs are idempotent.
- The fixture resets the local DB before each session; no state leaks between runs.

Resetting a Python application object inside a worker would not reset a separate server process;
the signed-cookie + SQLite design fixes the scaffold defect at its root.

## SUT lifecycle

- Local: `live_server` starts `python app/store.py` on `5100 + worker_index` and polls `/health`.
- Docker/CI: `EXTERNAL_SUT_URL` is set; fixtures poll `/health` of the already-started service.
- Cleanup is in `finally` blocks, so a failing test cannot leak a process.

## Compatibility note

The templates use Flask-style `url_for('static', filename=...)`; a small helper in `_ctx()` maps
this to FastAPI's static URL. `_render()` supports both the older and newer Starlette
`TemplateResponse` signatures so the same code runs with the locally pinned stack and the newer
versions resolved inside the Playwright container base image.

## Evidence pipeline

- Every test gets a fresh context with `record_video_dir`.
- Video handles are collected **before** `context.close()` (the page list is cleared on close).
- On a failed call phase, a full-page screenshot is captured and attached to the correct Allure
  result via the `pytest_runtest_makereport` hook.
- Artifact filenames include the full node ID, which makes parametrized cases unique.

## CI quality gates

`.github/workflows/ui-tests.yml` defines a `quality-check` job (Ruff lint, Ruff format check,
`mypy app tests`). All three browser matrix jobs declare `needs: quality-check`, so a browser job
never runs unless the quality gates pass.

## Browser selection

`BROWSER` sets `config.option.browser` as a list in `pytest_configure`, matching the
`pytest-playwright` CLI contract. Chromium, Firefox and WebKit are installed and exercised.

## Delivery

- Dockerfile: official Playwright Python image `v1.65.2-noble`, matching the pinned package.
- Compose: `storefront` (healthchecked, FastAPI + SQLite) and `tests` services on a private network.
- CI: real browser tests in a three-browser matrix with minimal `contents: read` permission.
