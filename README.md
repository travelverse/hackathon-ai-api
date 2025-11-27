Primary AI microservice for the 1World TravelVerse project.

This service exposes a FastAPI-based backend that provides:

-   **Profile extraction** – builds a structured travel profile from free-form text using Gemini.
-   **AI geocoding** – resolves noisy, multilingual location text into normalized names, coordinates and source URLs, powered by Gemini.

### Overview

`travelverse-ai-api` provides two core AI functions for the TravelVerse platform:

-   **Travel profile extraction**  
    Converts free-form, multilingual text into a structured traveler profile using Gemini.  
    Extracts interests, constraints, preferences and contextual information while guaranteeing a stable JSON schema.

-   **AI geocoding**  
    Interprets noisy or partial location text (any language), performs reasoning + web search,  
    and returns normalized place names, coordinates, country code, source URLs and locale-specific notes.

The microservice is optimized for:

-   reliable structured output,
-   multilingual understanding,
-   fault-tolerant extraction from imperfect user input,
-   clean JSON schemas for downstream systems.

### Architectural Overview

The service is a lightweight FastAPI-based microservice built around two Gemini-powered capabilities:

-   **API layer (FastAPI)**

    -   Provides `/api/profile/extract`, `/api/profile/geocode`, and `/api/health`
    -   Uses Pydantic for strict schema validation
    -   Uses `X-Guard-Token` for simple access control

-   **AI layer (Gemini 2.5 Flash)**

    -   Handles multilingual profile extraction
    -   Performs multilingual free-text geocoding with reasoning and web search
    -   Always returns structured JSON according to predefined schemas

-   **Configuration layer**
    -   Controlled through `settings.toml` and `.env`
    -   Includes service parameters, security settings, and Gemini service account configuration

This architecture keeps the service compact while delegating semantic reasoning to Gemini.

### Install

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

This creates `.venv` in the project root and installs all dependencies from `pyproject.toml` and `uv.lock`.

Create a `.env` file in the project root:

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

-   copy prepared `settings.toml` into project root
-   ensure `[service]`, `[security]` and `[genai]` sections are present
-   in `[genai]` configure:

```toml
[genai]
service_account_file = "/path/to/genai-sa-key.json"
```

Place `genai-sa-key.json` on the server.

Run the service:

```bash
./service.sh
```

After startup, the service can be checked at:

-   `http://{host}:{port}/api/health`
-   `http://{host}:{port}/api/profile/extract`
-   `http://{host}:{port}/api/profile/geocode`

### API endpoints

All endpoints are served under `/api` and protected by the `X-Guard-Token` header (see `[security]` in `settings.toml`).

#### `GET /api/health`

Simple health check, returns:

```json
{ "status": "ok" }
```

#### `POST /api/profile/extract`

Builds a structured travel preference profile from free-form text using Gemini.  
Input: multilingual unstructured text.  
Output: normalized JSON profile according to the service schema.

#### `POST /api/profile/geocode`

LLM-based geocoding: resolves noisy, multilingual free-text descriptions of locations into:

-   standardized place name (English),
-   resolved official name,
-   country code,
-   latitude & longitude,
-   source URLs used for grounding,
-   locale-specific notes.

### Architectural Overview

The service is a lightweight FastAPI-based microservice composed of three layers:

#### **API Layer (FastAPI)**

-   Exposes `/api/profile/extract`, `/api/profile/geocode`, and `/api/health`
-   Uses Pydantic for strict JSON schema validation
-   Protects endpoints with the `X-Guard-Token` header
-   Fully multilingual input support

#### **AI Layer (Gemini 2.5 Flash)**

-   Powers both profile extraction and geocoding
-   Performs multilingual understanding, reasoning and web search
-   Always outputs deterministic, strictly validated JSON
-   Handles ambiguity resolution and structured normalization

#### **Configuration Layer**

-   Controlled through `.env` and `settings.toml`
-   Defines service settings, security rules, and Gemini credentials
-   Keeps the microservice portable and environment-agnostic

This architecture keeps the service compact while delegating heavy semantic reasoning to Gemini.

### Features Overview

`travelverse-ai-api` provides two core AI capabilities for the TravelVerse platform:

#### **Travel Profile Extraction**

-   Converts free-form, multilingual user text into a structured travel profile
-   Extracts interests, constraints, preferences, budget signals, time hints and contextual intent
-   Powered by Gemini with guaranteed schema-safe JSON output
-   Resilient to noisy, incomplete or casually written input

#### **AI Geocoding**

-   Interprets noisy or partial location text in any language
-   Performs reasoning + web search to identify real places
-   Normalizes names into English, resolves coordinates, country, and source URLs
-   Handles explicit places, ambiguous locations, generic categories and full addresses
-   Produces locale-translated notes for use in UX flows

The microservice is optimized for:

-   reliable structured output,
-   multilingual understanding,
-   fault-tolerant processing of imperfect user input,
-   integration as a backend component in the broader TravelVerse system.

### API Endpoints

All endpoints are served under `/api` and protected by the `X-Guard-Token` header  
(configured in `[security]` of `settings.toml`).

#### **GET `/api/health`**

Simple health check.  
Returns:

```json
{ "status": "ok" }
```

#### **POST `/api/profile/extract`**

Builds a structured travel preference profile from free-form multilingual text using Gemini.  
Guarantees a stable JSON schema regardless of input quality.

#### **POST `/api/profile/geocode`**

LLM-based geocoding that:

-   processes noisy / partial / multilingual location queries,
-   performs reasoning + web search,
-   resolves the place into normalized English names, coordinates, metadata, and locale-translated notes.

### Contributing

This repository is currently optimized for internal development during the TravelVerse project.  
If you plan to extend or modify the service:

-   follow the existing project structure,
-   keep prompts and schemas under strict version control,
-   validate all Gemini outputs with Pydantic models,
-   ensure new endpoints are covered by lightweight integration tests.

Pull requests and extensions should preserve:

-   predictable JSON output,
-   stable schemas,
-   multilingual robustness,
-   reproducible geocoding behaviour.

### Development Notes

-   The service relies on **Gemini 2.5 Flash** with service-account authentication.
-   All AI behaviours (profile extraction and geocoding) are controlled by internal prompts stored in the codebase.
-   Geocoding includes web-search calls and a multi-stage reasoning pipeline; therefore responses may vary depending on real-time search results.
-   For local debugging, enable verbose logging in `settings.toml` and watch `app/logs/service.log`.

Recommended environment:

-   Python 3.11+
-   `uv` for dependency and venv management
-   FastAPI + Uvicorn for serving

### License

This project is released under the MIT License.  
See `LICENSE` for full details.
