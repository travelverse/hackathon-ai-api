# travelverse-ai-api

Primary AI microservice for the **1World TravelVerse** project.

This service exposes a FastAPI-based backend that provides:

-   **Profile extraction** – builds a structured travel profile from free-form multilingual text using Gemini.
-   **AI geocoding** – resolves noisy, multilingual location text into normalized names, coordinates, metadata and source URLs.

The microservice focuses on:

-   reliable structured JSON output,
-   multilingual understanding,
-   fault-tolerant processing of imperfect input,
-   clean schemas for downstream systems.

---

## Overview

`travelverse-ai-api` provides two core AI capabilities:

### **Travel Profile Extraction**

-   Converts arbitrary multilingual text into a structured traveler profile.
-   Extracts interests, constraints, preferences, budget signals, timing hints and contextual intent.
-   Always returns schema-validated JSON regardless of input quality.

### **AI Geocoding**

-   Interprets noisy or partial human-written location queries in any language.
-   Performs reasoning + web search to identify real places and addresses.
-   Returns:
    -   normalized English names,
    -   coordinates,
    -   country code,
    -   source URLs used by the model,
    -   translated locale-specific notes.
-   Handles specific locations, ambiguous cases, generic queries and precise addresses.

---

## Architectural Overview

The service is a lightweight FastAPI-based microservice composed of three layers:

### **1. API Layer (FastAPI)**

-   Exposes `/api/profile/extract`, `/api/profile/geocode`, and `/api/health`.
-   Uses **Pydantic** for strict JSON schema validation.
-   Protects endpoints using the `X-Guard-Token` header.
-   Accepts fully multilingual input.

### **2. AI Layer (Gemini 2.5 Flash)**

-   Drives both profile extraction and geocoding.
-   Performs multilingual understanding, reasoning and web search.
-   Always produces deterministic, strictly validated JSON outputs.
-   Handles ambiguity resolution and structured normalization.

### **3. Configuration Layer**

-   Controlled through `.env` and `settings.toml`.
-   Defines service settings, security rules and Gemini service-account credentials.
-   Keeps the service environment-agnostic and portable.

---

## Install

Clone the source repository.

Install `uv` (Python package/venv manager):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

Create a virtual environment and install dependencies:

```bash
uv sync
```

This creates `.venv` in the project root and installs dependencies from `pyproject.toml` and `uv.lock`.

Create a `.env` file:

```bash
APP_ROOT=$(pwd)
cat > .env <<EOF
APP_MODE=development
APP_ROOT="$APP_ROOT"
APP_DEPRECATIONS=false

TZ=UTC
EOF
```

Configure `settings.toml`:

-   Copy prepared `settings.toml` into the project root
-   Ensure `[service]`, `[security]`, and `[genai]` sections exist
-   Configure the Gemini service account in `[genai]`:

```toml
[genai]
service_account_file = "/path/to/genai-sa-key.json"
```

Place `genai-sa-key.json` on the server.

Run the service:

```bash
./service.sh
```

Check that it is running:

-   `http://{host}:{port}/api/health`
-   `http://{host}:{port}/api/profile/extract`
-   `http://{host}:{port}/api/profile/geocode`

---

## API Endpoints

All endpoints are served under `/api` and protected by the `X-Guard-Token` header  
(configured in `[security]` of `settings.toml`).

### **GET `/api/health`**

Simple health check.  
Returns:

```json
{ "status": "ok" }
```

### **POST `/api/profile/extract`**

Builds a structured travel preference profile from free-form multilingual text using Gemini.  
Always returns a stable JSON schema.

### **POST `/api/profile/geocode`**

LLM-based geocoding that:

-   processes noisy / partial / multilingual input,
-   performs reasoning + web search,
-   resolves the place into normalized English names,
-   returns coordinates, metadata and locale-translated notes.

---

## Contributing

This repository is currently optimized for internal development within the TravelVerse project.

If extending the service:

-   keep prompts and schemas under strict version control,
-   validate all Gemini outputs with Pydantic models,
-   preserve deterministic JSON structure,
-   ensure new endpoints include lightweight integration tests,
-   maintain multilingual robustness.

---

## Development Notes

-   Powered by **Gemini 2.5 Flash** with service-account authentication.
-   All AI prompts are embedded inside the codebase for reproducibility.
-   Geocoding uses reasoning + web search; responses may vary based on real-time search results.
-   Enable verbose logs in `settings.toml` and read `app/logs/service.log` for debugging.

Recommended environment:

-   Python 3.11+
-   `uv` for dependency and venv management
-   FastAPI + Uvicorn for serving
