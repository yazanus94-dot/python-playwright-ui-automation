# Python + Playwright Professional UI Automation Framework

A portfolio-grade end-to-end UI automation framework for **ShopEase**, a real stateful Flask
storefront. The suite exercises genuine customer journeys in Chromium, Firefox and WebKit using
the Page Object Model, session-isolated server-side state, parallel execution and Allure evidence.

## 1. Project purpose

Demonstrate mid-level QA Automation / SDET engineering: a working system under test, maintainable
page objects, meaningful business assertions, cross-browser execution, deterministic parallel
runs, containerised execution, CI reporting and honest verification evidence.

## 2. Technology stack

| Component | Version used locally |
|---|---|
| Python | 3.14.7 (Python 3.12 unavailable locally; CI targets 3.12) |
| Flask / Jinja2 | 3.x / 3.x |
| Playwright Python | 1.65.2 |
| pytest | 8.4.2 |
| pytest-playwright | 0.10.0 |
| pytest-xdist | 3.8.0 |
| allure-pytest | 2.16.2 |
| Ruff | 0.8.6 |
| Allure CLI | 2.46.1 (npm) |
| Java | 26.0.2.1 |
| Docker / Compose | 29.9.3 / v5.7.0 |

## 3. Architecture

```
Browser context (per test, isolated cookies)
        |
Page Objects (locators + actions only)
        |
Playwright sync API -> HTTP -> Flask SUT (app/store.py)
        |
Server-side state keyed by opaque sid cookie (CARTS / ORDERS / USERS)
```

The SUT is a separate process in local runs (`tests/conftest.py`) and a separate container in
Compose/CI. A sid is generated server-side and stored in the signed session cookie, so independent
browser contexts cannot read or mutate each other's carts or orders. `EXTERNAL_SUT_URL` points the
fixtures at an already running storefront (Docker/CI); otherwise a per-worker local process starts
on port `5100 + worker_index` and is awaited via `/health`.

## 4. Directory structure

```
app/
  store.py, main.py            # stateful storefront and health endpoint
  templates/, static/          # UI under test
config/settings.py             # environment-driven configuration
tests/
  conftest.py                  # server, contexts, evidence, fixtures
  pages/                       # BasePage, Catalog, Product, Cart, Checkout,
                               # Login, Register, Orders, Confirmation
  test_*.py                    # 70 collected cases across 7 modules
docs/                          # ARCHITECTURE, TEST_STRATEGY, TEST_CASES, TRACEABILITY
.github/workflows/ui-tests.yml # 3-browser CI matrix
Dockerfile, docker-compose.yml
```

## 5. Installation

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m playwright install chromium firefox webkit
```

## 6. Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m playwright install chromium firefox webkit
$env:BROWSER = "chromium"
python -m pytest -v
```

## 7. Linux / macOS

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m playwright install --with-deps chromium firefox webkit
BROWSER=chromium python -m pytest -v
```

## 8. Demo application startup

```bash
python -m app.main
curl http://127.0.0.1:5000/health
```

## 9. Running tests

```bash
python -m pytest -v
python -m pytest -m smoke -v
python -m pytest -m regression -v
python -m pytest -m negative -v
```

The fixtures start and stop the SUT automatically; no manual server is needed locally.

## 10. Running tests per browser

```powershell
$env:BROWSER="chromium"; python -m pytest -v
$env:BROWSER="firefox";  python -m pytest -v
$env:BROWSER="webkit";   python -m pytest -v
```

## 11. Parallel execution

```bash
python -m pytest -n 2 -v
```

Each xdist worker gets its own server port and browser contexts; session isolation keeps state
separate. Parallel execution was not disabled to hide failures.

## 12. Allure report generation

```bash
allure generate allure-results --clean -o allure-report
allure open allure-report
```

Verified with Allure CLI **2.46.1** and Java **26.0.2.1**. The HTML report was generated
successfully from 2,115 result files produced by the final browser verification runs.

## 13. Screenshot and video evidence

Failure screenshots are written to `artifacts/screenshots/`, videos to `artifacts/videos/`, and
both are attached to Allure. A temporary intentional-failure probe verified **1 PNG + 1 WEBM**
attachment. Final green runs produced 198 videos and no failure screenshots (expected).

## 14. Docker

```bash
docker compose config --quiet
docker compose build
docker compose up -d storefront
docker compose run --rm tests
docker compose down -v
```

The `tests` service waits for `storefront` health and uses `EXTERNAL_SUT_URL=http://storefront:5000`.
Reports are bind-mounted to `./reports`, `./allure-results` and `./artifacts`.

## 15. GitHub Actions

`.github/workflows/ui-tests.yml` runs on push, pull request and manual dispatch. It installs pinned
dependencies and the selected browser with OS libraries, starts the app, polls `/health` up to 60
seconds, runs real browser tests with `-n 2`, always stops the app, and uploads reports, Allure
results, screenshots and videos even on failure. Matrix: chromium, firefox, webkit.

## 16. Test coverage summary

70 cases: catalogue/homepage (17), product details (14), negative scenarios (11), cart (8),
authentication (8), checkout/orders (8), session isolation (4). See `docs/TEST_CASES.md`.

## 17. Actual verification results

| Check | Actual result |
|---|---|
| `python -m compileall -q app tests` | exit 0 |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 25 files already formatted |
| `pytest --collect-only -q` | 70 tests collected |
| `pytest -m smoke -v` | 7 passed, 63 deselected |
| `pytest -m regression -v` | 70 passed |
| `pytest -n 2 -v` | 70 passed |
| Chromium full suite | 70 passed |
| Firefox full suite | 70 passed |
| WebKit full suite | 70 passed |
| Allure HTML report | generated, exit 0 |
| Docker Compose config | exit 0 |
| Docker Compose build | both images built |
| `docker compose run --rm tests` | 70 passed in 19.03s |
| `docker compose down -v` | exit 0 |

## 18. Known limitations

- Python 3.12 is not installed locally (only 3.14.7); local diagnostics used 3.14.7 while CI is
  pinned to 3.12. No 3.12-only syntax is used.
- `pytest-asyncio` emits deprecation warnings from third-party code; tests do not use asyncio.
- Videos are always recorded; failure screenshots are captured on failure only.
- No credentials or tokens are stored in the repository; `.env` and generated artifacts are ignored.
