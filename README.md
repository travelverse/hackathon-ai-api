````markdown
# travelverse-ai-api

Primary TravelVerse AI API microservice.

Contains following services:
- service: TravelVerse AI API service. Gemini-based profile extraction & geocoding

### Install

1. clone source repository

````

2. install `uv` (Python package/venv manager)

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv --version
   ```

3. create virtual environment and install dependencies

   ```bash
   uv sync
   ```

   This will create `.venv` in the project root and install all dependencies from `pyproject.toml` and `uv.lock`.

4. create `.env` file in project root

   ```bash
   APP_ROOT=$(pwd)
   cat > .env <<EOF
   APP_MODE=development
   APP_ROOT="$APP_ROOT"
   APP_DEPRECATIONS=false

   TZ=UTC
   EOF
   ```

5. configure `settings.toml`

   * copy prepared `settings.toml` into project root

   * ensure `[service]`, `[security]` and `[genai]` sections are present

   * in `[genai]` section configure:

     ```toml
     [genai]
     service_account_file = "/path/to/genai-sa-key.json"
     ```

   * place `genai-sa-key.json` on the server

6. run service using `service.sh`

   ```bash
   ./service.sh
   ```

   After startup, service can be checked by fetching:

   * `http://{host}:{port}/api/health`
   * `http://{host}:{port}/api/profile/extract`
   * `http://{host}:{port}/api/profile/geocode`


### API endpoints

All endpoints are served under `/api` and protected by `X-Guard-Token` header (see `[security]` in `settings.toml`):

* `GET /api/health`
  Simple health check, returns `{"status": "ok"}`.

* `POST /api/profile/extract`
  Builds structured travel preference profile from free text using Gemini.

* `POST /api/profile/geocode`
  LLM-based geocoding: resolves free-form location text into normalized name, country code, latitude/longitude and source URLs.

### Update

Steps to update application:

1. update source code

   ```bash
   git pull
   ```

2. update environment

   ```bash
   uv sync
   ```

   This will apply dependency changes from `pyproject.toml` / `uv.lock`.

3. restart service (NOT TESTED!!!)

   * if running under supervisor:

     ```bash
     sudo supervisorctl restart service:
     ```

