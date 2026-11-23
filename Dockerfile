# Playwright Python image bundles the OS libraries required by Chromium,
# Firefox and WebKit. The tag must match the pinned playwright version.
FROM mcr.microsoft.com/playwright/python:v1.65.2-noble

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

RUN mkdir -p allure-results artifacts/screenshots artifacts/videos reports

EXPOSE 5000

CMD ["python", "-m", "app.main"]
