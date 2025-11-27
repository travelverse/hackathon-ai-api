# app/modules/genai.py
# -*- coding: utf-8 -*-

from functools import lru_cache
import json
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Tuple


import system

from google import genai
from google.oauth2 import service_account
from google.genai.types import (
    GenerateContentConfig,
    Content,
    Part,
    Type,
    Schema,
    Tool,
    GoogleSearch,
    ToolConfig,
    FunctionCallingConfig,
    FunctionCallingConfigMode,
    ThinkingConfig,
)


@lru_cache()
def get_genai_client() -> genai.Client:
    cfg = getattr(system.settings, "genai", {})

    service_account_file = cfg.get("service_account_file")
    project = cfg.get("project")
    location = cfg.get("location", "us-central1")

    if not service_account_file or not project:
        raise RuntimeError("genai config is incomplete (service_account_file/project)")

    creds = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    client = genai.Client(
        vertexai=True,
        credentials=creds,
        project=project,
        location=location,
    )

    return client


class UserProfile(BaseModel):
    travelMode: Optional[str] = None
    budgetPreference: Optional[int] = None
    crowdPreference: Optional[int] = None
    hiddenGemPreference: int = 2

    entityTypeIds: List[int] = Field(default_factory=list)
    excludedEntityTypeIds: List[int] = Field(default_factory=list)

    entityTypeValues: List[str] = Field(default_factory=list)
    excludedEntityTypeValues: List[str] = Field(default_factory=list)

    notes: str = ""


VALUE_TO_ID = {'Artefact': 1, 'Square': 2, 'Cascade Complex': 3, 'Museum': 4, 'Theater': 5, 'Mosque': 6, 'Cathedral': 7, 'Church': 8,
               'Market': 9, 'Fort': 10, 'Old town': 11, 'Gates': 12, 'Beach': 13, 'Park': 14, 'Natural wonder': 15, 'City': 16,
               'Archaeological site': 17, 'Village': 19, 'Fortress': 20, 'Bridge': 21, 'Palace': 22, 'Sulfur baths': 23, 'Hotel': 25,
               'City Hall': 26, 'Fountain': 27, 'Embankment': 28, 'Port': 29, 'Street': 30, 'Railway station': 31, 'Lift/Elevator': 32,
               'Arch': 33, 'Viewpoint': 34, 'Castle': 35, 'Art gallery': 36, 'Circus': 37, 'Priory': 38, 'Artist': 39,
               'Historical site': 40, 'Synagogue': 41, 'Gallery': 42, 'Cable car': 43, 'Cafe': 44, 'Restaurant': 45, 'Bar': 46,
               'Coffee shop': 47, 'Store': 48, 'Boutique': 49, 'Library': 50, 'University': 51, 'Hospital': 52, 'Stadium': 53,
               'Island': 54, 'Landmark': 55, 'Exhibition Centre': 57, 'Beach Promenade': 58, 'Nature Landmark': 59, 'Luxury Shopping': 60,
               'Pavilion': 61, 'Exhibition': 62, 'Highlight': 63, 'Lake': 64, 'Monument': 65, 'Statue': 66, 'Spa': 67,
               'Your unique place': 68, 'Hotel Amenities': 69, 'Station': 70, 'Concert': 71, 'Event': 72, 'Temple': 73, 'Monastery': 74,
               'Shrine': 75, 'Chapel': 76, 'Basilica': 77, 'Pagoda': 78, 'Sacred Site': 79, 'Pilgrimage Site': 80, 'Historic Building': 81,
               'Opera House': 82, 'Tower': 83, 'Skyscraper': 84, 'Clock Tower': 85, 'Observation Tower': 86, 'Ruins': 87, 'Tomb': 88,
               'Heritage Site': 89, 'Cultural Center': 90, 'Memorial': 91, 'Public Art': 92, 'Neighborhood': 93, 'Promenade': 94,
               'Pedestrian Street': 95, 'Lookout Point': 96, 'Waterfall': 97, 'Mountain': 98, 'Canyon': 99, 'Cave': 100, 'Valley': 101,
               'Waterfront': 102, 'River': 103, 'Botanical Garden': 104, 'National Park': 105, 'Forest': 106, 'Hiking Trail': 107,
               'Cinema': 108, 'Night Club': 109, 'Music Venue': 110, 'Amusement Park': 111, 'Zoo': 112, 'Aquarium': 113,
               'Festival Ground': 114, 'Observation Deck': 115, 'Historic Train (touristic experience)': 116, 'Funicular': 117,
               'Pub': 118, 'Brewery': 119, 'Winery': 120, 'Bakery': 121, 'Food Court': 122, 'Street Food': 123, 'Rooftop Bar': 124,
               'Wine Bar': 125, 'Tea House': 126, 'Food Market': 127, 'Shopping Mall': 128, 'Souvenir Shop': 129, 'Antique Shop': 130,
               'Craft Market': 131, 'Flea Market': 132, 'Department Store': 133, 'Designer Store': 134, 'Bookstore': 135, 'Art Shop': 136,
               'Resort Spa': 137, 'Hot Spring': 138, 'Hammam': 139, 'Wellness Center': 140, 'Yoga Studio': 141, 'Massage Center': 142,
               'Onsen': 143, 'Day Spa': 144}

VALUE_ENUM: List[str] = list(VALUE_TO_ID.keys())

profile_schema = Schema(
    type=Type.OBJECT,
    properties={
        "travelMode": Schema(
            type=Type.STRING,
            enum=["walk", "car", "bike", "public_transport"],
            nullable=True,
        ),
        "budgetPreference": Schema(
            type=Type.INTEGER,
            minimum=1,
            maximum=5,
            nullable=True,
        ),
        "crowdPreference": Schema(
            type=Type.INTEGER,
            minimum=1,
            maximum=3,
            nullable=True,
        ),
        "hiddenGemPreference": Schema(
            type=Type.INTEGER,
            minimum=1,
            maximum=3,
            nullable=True,
        ),
        "entityTypeValues": Schema(
            type=Type.ARRAY,
            items=Schema(type=Type.STRING),
            nullable=True,
        ),
        "excludedEntityTypeValues": Schema(
            type=Type.ARRAY,
            items=Schema(type=Type.STRING),
            nullable=True,
        ),
        "notes": Schema(
            type=Type.STRING,
            nullable=True,
        ),
        "resetTravelMode": Schema(
            type=Type.BOOLEAN,
            nullable=True,
        ),
        "resetBudgetPreference": Schema(
            type=Type.BOOLEAN,
            nullable=True,
        ),
        "resetEntityTypeValues": Schema(
            type=Type.BOOLEAN,
            nullable=True,
        ),
        "replaceEntityTypeValues": Schema(
            type=Type.BOOLEAN,
            nullable=True,
        ),
    },
    required=[],
)

EXTRACT_CFG = GenerateContentConfig(
    temperature=0.0,
    top_p=1.0,
    candidate_count=1,
    seed=7,
    response_mime_type="application/json",
    response_schema=profile_schema,
)


def extract_full_profile(text: str, locale: str, return_values: bool = False) -> dict:
    """
    Single-step extractor: build a structured user profile from free text.

    The model returns:
      - travelMode, budgetPreference, crowdPreference, hiddenGemPreference, notes
      - entityTypeValues: types of places the user LIKES / is interested in
      - excludedEntityTypeValues: types of places the user explicitly DISLIKES or wants to avoid
      - resetBudgetPreference, resetTravelMode, resetEntityTypeValues (optional flags for explicit indifference)

    Both lists are strings; we map them to numeric IDs via VALUE_TO_ID.
    Inside a single delta:
      - if the same value appears in both lists, we treat it as DISLIKED (exclude wins),
        but log the conflict.
    """

    taxonomy_text = "\n".join(f"- {v}" for v in VALUE_ENUM)

    instruction = (
        "You are a travel assistant AI. Based on the user's description, "
        "extract their travel preferences into a structured profile defined by the system schema.\n\n"

        "Allowed place type values (Value) are exactly the following case-sensitive strings:\n"
        f"{taxonomy_text}\n\n"

        "Semantics:\n"
        "- entityTypeValues: place types the user likes, is interested in, or would enjoy visiting.\n"
        "- excludedEntityTypeValues: place types the user explicitly dislikes, avoids, "
        "  or does not want to visit.\n\n"

        "Rules for place types:\n"
        "- Extract only what is explicitly stated or strongly implied.\n"
        "- For entityTypeValues you may include indirect but well-supported preferences "
        "  (for example: love of history, architecture, viewpoints, cozy local coffee places).\n"
        "- For excludedEntityTypeValues include ONLY clear negative attitude or refusal "
        "  (for example: 'I hate museums', 'I never go to stadiums', 'I don't want malls').\n"
        "- Do NOT infer dislikes from preferences alone "
        "  (no logic like 'they like quiet places so they must hate stadiums').\n"
        "- When both specific and generic Values apply, prefer the more specific ones and avoid duplicates.\n\n"

        "Scalar fields:\n"
        "- travelMode: set only if the text clearly indicates a preference for walking, car, bike "
        "  or public transport.\n"
        "- budgetPreference (1–5): infer the user's price comfort level when the text provides a clear signal; "
        "  if there is no signal about money or prices, leave it null.\n"
        "- crowdPreference (1–3): infer the user's comfort with crowds and lively vs quiet places when the text "
        "  provides a clear signal; if there is no signal about crowds or atmosphere, leave it null.\n"
        "- hiddenGemPreference (1–3): infer the user's attitude toward popular vs hidden locations:\n"
        "    1 → prefers hidden, local, less touristy places;\n"
        "    2 → neutral when there is no clear signal;\n"
        "    3 → prefers famous, popular, iconic must-see places.\n"
        "  Use 1 or 3 whenever the text gives even a weak but meaningful hint; use 2 only when no relevant signals exist.\n\n"

        "Exclusive place-type preferences:\n"
        "- If the user clearly states that they want ONLY specific place types and do not want any other types suggested, "
        "treat those types as an exclusive list.\n"
        "- In that case, put exactly those types into entityTypeValues and set replaceEntityTypeValues to true.\n"
        "- In all other cases, treat entityTypeValues as additive preferences and do not set replaceEntityTypeValues.\n\n"



        "Explicit indifference:\n"
        "- If the user clearly states that they do not care about budget, travel mode, or place types, "
        "  set the corresponding reset flags ('resetBudgetPreference', 'resetTravelMode', 'resetEntityTypeValues') "
        "  to true and do not set new values for these fields.\n\n"

        "General:\n"
        "- Do not fabricate information that is not supported by the text.\n"
        "- Return a single valid JSON object only, with no extra text."
    )

    client = get_genai_client()
    cfg = getattr(system.settings, "genai", {})
    model_name = cfg.get("extract_model", "gemini-2.5-flash")
    resp = client.models.generate_content(
        model=model_name,
        contents=[
            Content(
                role="user",
                parts=[
                    Part(text=instruction),
                    Part(text=f"User text: {text}"),
                ],
            )
        ],
        config=EXTRACT_CFG,
    )

    try:
        parts = resp.candidates[0].content.parts
        raw = "".join(p.text for p in parts if getattr(p, "text", None))
        data = json.loads(raw) if raw else {}
    except Exception as e:
        print("extract_full_profile parse error:", e)
        data = {}

    travelMode = data.get("travelMode")
    budgetPreference = data.get("budgetPreference")
    crowdPreference = data.get("crowdPreference")
    hiddenGemPreference = data.get("hiddenGemPreference")
    notes = (data.get("notes") or "").strip()

    resetTravelMode = data.get("resetTravelMode")
    resetBudgetPreference = data.get("resetBudgetPreference")
    resetEntityTypeValues = data.get("resetEntityTypeValues")

    like_values = data.get("entityTypeValues") or []
    dislike_values = data.get("excludedEntityTypeValues") or []

    recognized_like_ids = set()
    recognized_dislike_ids = set()

    for v in like_values:
        if v in VALUE_TO_ID:
            recognized_like_ids.add(VALUE_TO_ID[v])
        else:
            if v:
                print(f"[unknown like Value] {v!r}")

    for v in dislike_values:
        if v in VALUE_TO_ID:
            recognized_dislike_ids.add(VALUE_TO_ID[v])
        else:
            if v:
                print(f"[unknown dislike Value] {v!r}")

    conflicts = recognized_like_ids.intersection(recognized_dislike_ids)
    if conflicts:
        print(f"[delta conflict] IDs in both like & dislike: {sorted(conflicts)}")
        recognized_like_ids -= conflicts

    entityTypeIds = sorted(recognized_like_ids)
    excludedEntityTypeIds = sorted(recognized_dislike_ids)
    replace_entity_type_values = bool(data.get("replaceEntityTypeValues"))

    result = {
        "travelMode": travelMode if travelMode in ["walk", "car", "bike", "public_transport"] else None,
        "budgetPreference": (
            int(budgetPreference)
            if isinstance(budgetPreference, (int, float)) and 1 <= int(budgetPreference) <= 5
            else None
        ),
        "crowdPreference": (
            int(crowdPreference)
            if isinstance(crowdPreference, (int, float)) and 1 <= int(crowdPreference) <= 3
            else None
        ),
        "hiddenGemPreference": (
            int(hiddenGemPreference)
            if isinstance(hiddenGemPreference, (int, float)) and 1 <= int(hiddenGemPreference) <= 3
            else None
        ),
        "entityTypeIds": entityTypeIds,
        "excludedEntityTypeIds": excludedEntityTypeIds,
        "notes": notes,
        "resetTravelMode": bool(resetTravelMode),
        "resetBudgetPreference": bool(resetBudgetPreference),
        "resetEntityTypeValues": bool(resetEntityTypeValues),
        "replaceEntityTypeValues": replace_entity_type_values,
    }

    if return_values:
        inv_map = {v_id: v for v, v_id in VALUE_TO_ID.items()}
        result["entityTypeValues"] = [inv_map[i] for i in entityTypeIds]
        result["excludedEntityTypeValues"] = [inv_map[i] for i in excludedEntityTypeIds]
    return result



def apply_profile_delta(state: UserProfile, delta: dict) -> UserProfile:
    """
    Apply a structured delta update to an existing UserProfile.

    This function receives the current profile state and a delta dictionary
    generated by the LLM. It merges the delta into the state following
    strict update rules to ensure deterministic, conflict-free behavior.

    Update rules implemented:

    • Reset flags
      If the delta contains resetTravelMode, resetBudgetPreference, or
      resetEntityTypeValues, the corresponding fields are cleared before
      applying other updates.

    • Scalar fields
      travelMode, budgetPreference, and crowdPreference are overwritten only
      when delta provides a valid value.
      hiddenGemPreference accepts only values {1, 3}; a value of 2 is treated
      as “no change”.

    • Entity preferences (likes/dislikes)
      The function merges entityTypeIds (likes) and excludedEntityTypeIds
      (dislikes) as sets:
        – new likes are added and removed from the dislike list
        – new dislikes are added and removed from the like list
      If replaceEntityTypeValues is true, the existing like set is replaced
      entirely with the new like set.

    • Notes
      If delta contains a non-empty notes field, it replaces the existing notes.

    • Value→ID synchronization
      entityTypeValues and excludedEntityTypeValues are recalculated from the
      canonical VALUE_TO_ID mapping to keep the string and numeric representations
      consistent.

    Returns:
        A new UserProfile instance with all updates applied.
    """
    data = state.model_dump()

    if delta.get("resetTravelMode"):
        data["travelMode"] = None

    if delta.get("resetBudgetPreference"):
        data["budgetPreference"] = None

    if delta.get("resetEntityTypeValues"):
        data["entityTypeIds"] = []
        data["excludedEntityTypeIds"] = []

    tm = delta.get("travelMode")
    if tm in ["walk", "car", "bike", "public_transport"]:
        data["travelMode"] = tm

    bp = delta.get("budgetPreference")
    if isinstance(bp, (int, float)):
        ibp = int(bp)
        if 1 <= ibp <= 5:
            data["budgetPreference"] = ibp

    cp = delta.get("crowdPreference")
    if isinstance(cp, (int, float)):
        icp = int(cp)
        if 1 <= icp <= 3:
            data["crowdPreference"] = icp

    hgp = delta.get("hiddenGemPreference")
    if isinstance(hgp, (int, float)):
        ihgp = int(hgp)
        if ihgp in (1, 3):
            data["hiddenGemPreference"] = ihgp

    current_likes = set(data.get("entityTypeIds", []))
    current_dislikes = set(data.get("excludedEntityTypeIds", []))

    def to_int_set(seq) -> set[int]:
        if not seq:
            return set()
        res = set()
        for v in seq:
            if isinstance(v, int):
                res.add(v)
            elif isinstance(v, float) and v.is_integer():
                res.add(int(v))
            elif isinstance(v, str) and v.isdigit():
                res.add(int(v))
        return res

    new_likes = to_int_set(delta.get("entityTypeIds"))
    new_dislikes = to_int_set(delta.get("excludedEntityTypeIds"))

    replace_likes = delta.get("replaceEntityTypeValues") is True

    if new_likes:
        if replace_likes:
            current_likes = set(new_likes)
            current_dislikes -= new_likes
        else:
            current_likes |= new_likes
            current_dislikes -= new_likes

    if new_dislikes:
        current_dislikes |= new_dislikes
        current_likes -= new_dislikes

    data["entityTypeIds"] = sorted(current_likes)
    data["excludedEntityTypeIds"] = sorted(current_dislikes)

    new_notes = (delta.get("notes") or "").strip()
    if new_notes:
        data["notes"] = new_notes

    inv_map = {v_id: v for v, v_id in VALUE_TO_ID.items()}
    data["entityTypeValues"] = [inv_map[i] for i in data["entityTypeIds"] if i in inv_map]
    data["excludedEntityTypeValues"] = [
        inv_map[i] for i in data["excludedEntityTypeIds"] if i in inv_map
    ]
    return UserProfile(**data)

def generate_notes_from_profile(state: UserProfile, locale: str = "en") -> str:
    """
    Generates a human-readable notes summary based on the current user profile.
    Operates on an already assembled UserProfile rather than raw input text.
    """

    client = get_genai_client()
    cfg = getattr(system.settings, "genai", {})
    model_name = cfg.get("extract_model", "gemini-2.5-flash")

    inv_map = {v_id: v for v, v_id in VALUE_TO_ID.items()}
    like_values = [
        inv_map[i] for i in state.entityTypeIds if i in inv_map
    ] or state.entityTypeValues or []
    dislike_values = [
        inv_map[i] for i in state.excludedEntityTypeIds if i in inv_map
    ] or state.excludedEntityTypeValues or []

    profile_for_llm = {
        "travelMode": state.travelMode,
        "budgetPreference": state.budgetPreference,
        "crowdPreference": state.crowdPreference,
        "hiddenGemPreference": state.hiddenGemPreference,
        "entityTypeValues": like_values,
        "excludedEntityTypeValues": dislike_values,
    }

    profile_json = json.dumps(profile_for_llm, ensure_ascii=False)

    prompt = f"""
    You are a travel profile summarization assistant.

    Locale for output: "{locale}"

    You receive a structured user travel profile as JSON.
    Your task is to generate a short, natural, human-readable message that summarizes the user's overall travel preferences based on this profile.

    Field semantics (for your internal reasoning only; do not mention field names or numbers):
    - travelMode: walk = prefers exploring on foot; car = prefers driving; bike = enjoys cycling; public_transport = uses buses/metro.
    - budgetPreference (1–5): 1 = very price-sensitive; 3 = comfortable with average prices; 5 = willing to spend more for quality.
    - crowdPreference (1–3): 1 = prefers quiet places; 2 = neutral; 3 = enjoys lively, busy areas.
    - hiddenGemPreference (1–3): 1 = favors hidden, local, less-touristy spots; 2 = neutral; 3 = prefers iconic popular attractions.
    - If any field is null, simply omit this aspect from the description.

    Requirements:
    - Write the message strictly in the language corresponding to the locale above. Do not use any other language.
    - The message must be polite and suitable to show directly to the user.
    - Do not refer to yourself in the first person ("I", "we").
    - Do not mention JSON field names, IDs, or technical terms.
    - Do not show raw numeric values; describe them in natural language instead.
    - Focus on what the user seems to like, what they avoid, how they prefer to move around the city, and their attitude to budget, crowds, and popular vs hidden places.
    - Keep the message concise: about 2–4 short sentences.
    - The output must be plain text only, without JSON or any surrounding quotes.

    User profile JSON:
    {profile_json}
    """.strip()

    try:
        resp = client.models.generate_content(
            model=model_name,
            contents=[Content(role="user", parts=[Part(text=prompt)])],
            config=GenerateContentConfig(
                temperature=0.5,
                top_p=0.8,
                candidate_count=1,
                response_mime_type="text/plain",
            ),
        )

        parts = resp.candidates[0].content.parts
        text = "".join(getattr(p, "text", "") for p in parts if getattr(p, "text", None))
        return (text or "").strip()

    except Exception as e:  # noqa: BLE001
        system.logger.exception(f"generate_notes_from_profile error: {e}")
        return (state.notes or "").strip()


def update_profile_from_text(
    text: str,
    locale: str,
    state: UserProfile,
    return_values: bool = False,
) -> tuple[UserProfile, dict]:
    """
    High-level coordinator for updating the user's travel profile from free-text input.

    Behavior:
    - If `text` is empty or whitespace:
        • Do not run extraction or apply any updates.
        • Regenerate notes from the existing profile state only.
        • Return the unchanged state and an empty delta.

    - If `text` is provided:
        • Extract a structured delta using `extract_full_profile`.
        • Apply the delta to the current profile via `apply_profile_delta` to produce `new_state`.
        • Optionally rehydrate string-based entity type values when `return_values=True`.
        • Always regenerate notes based on the updated profile.

    Returns:
        (new_state, delta) — the updated UserProfile and the extracted delta dictionary.
    """

    if not text or not text.strip():
        new_state = state
        new_state.notes = generate_notes_from_profile(new_state, locale=locale)
        return new_state, {}

    delta = extract_full_profile(text, locale=locale, return_values=return_values)
    new_state = apply_profile_delta(state, delta)

    if return_values:
        inv_map = {v_id: v for v, v_id in VALUE_TO_ID.items()}

        new_state.entityTypeValues = [
            inv_map[i] for i in new_state.entityTypeIds if i in inv_map
        ]
        new_state.excludedEntityTypeValues = [
            inv_map[i] for i in new_state.excludedEntityTypeIds if i in inv_map
        ]
    else:
        new_state.entityTypeValues = []
        new_state.excludedEntityTypeValues = []

    new_state.notes = generate_notes_from_profile(new_state, locale=locale)

    return new_state, delta


geocode_schema = {
    "type": "OBJECT",
    "additionalProperties": False,
    "properties": {
        "standardizedQuery": {"type": "STRING"},
        "resolvedName": {"type": "STRING"},
        "countryCode": {"type": "STRING", "nullable": True},
        "lat": {"type": "NUMBER", "nullable": True},
        "lon": {"type": "NUMBER", "nullable": True},
        "sourceUrls": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
        },
        "notes": {"type": "STRING"},
    },
}


GEOCODE_CFG = GenerateContentConfig(
    temperature=0.0,
    response_mime_type="application/json",
    top_p=1.0,
    candidate_count=1,
    seed=7,
    response_schema=geocode_schema,
    # tools=[Tool(google_search=GoogleSearch())]
)

def geocode_with_gemini(place_query: str, locale: str = "en") -> Dict[str, Any]:
    """
    Resolve a free-form place query to a structured geocoding result using Gemini.

    The function sends a carefully constrained prompt to a Gemini model configured
    for geocoding and web-grounded lookup. The model is instructed to:
      - Interpret the user query, normalize it in English and decide whether it
        refers to a specific place or only to a generic type of place.
      - For generic queries, return a “no coordinates” result with
        lat = null, lon = null, notes = "" and an empty sourceUrls list.
      - For specific places, use web search to identify one real location, choose
        a canonical name, and return its coordinates, ISO country code and a small
        set of source URLs.
      - Produce a locale-aware human-readable notes field when coordinates are known
        (e.g. "<city>, <country>" translated to the target locale).

    On success, returns a dict compatible with GeocodeResponse:
        {
          "standardizedQuery": str,
          "resolvedName": str,
          "countryCode": str | None,
          "lat": float | None,
          "lon": float | None,
          "sourceUrls": list[str],
          "notes": str,
        }

    On any error (model failure, parsing issues, empty response), logs the exception
    and returns an error dict:
        {
          "error": "...",
          "input_query": place_query,
        }
    """
    client = get_genai_client()
    cfg = getattr(system.settings, "genai", {})
    model_name = cfg.get("geocode_model", "gemini-2.5-flash")

    prompt = f"""
    You are a geocoding assistant for a tourist application.

    Input place query: "{place_query}"
    Target locale: "{locale}"

    Your task:

    1) First, internally translate the input query into English. Use ONLY the English version for normalization and web search. The translation step is internal and must not appear in the JSON output.

    2) Decide whether the query refers to one specific identifiable place or only to a general category of place. You may use both direct and clear indirect cues, but do not force a specific place when the meaning remains ambiguous and no single real location is strongly indicated.

    3) For generic queries:
       • Do not try to guess a specific location.
       • Do not perform targeted web search for coordinates.
       • Set lat=null, lon=null, notes="", sourceUrls=[] and still return a valid JSON object.

    4) For specific places:
       • Always use web search to identify one real location and its coordinates. Do not rely on memorized knowledge.
       • Use reliable sources such as Wikipedia, web maps, encyclopedias or official portals.
       • If several locations share the same name:
           – If the query text clearly indicates a country, region or city, follow that.
           – Otherwise prefer the internationally well-known tourist destination.
       • Based on the English interpretation and web search, construct a concise standardizedQuery in English and choose a clear official name for resolvedName.
       • Provide a small list of relevant sourceUrls.

    5) Filling notes:
       • If lat or lon is null, notes must be exactly "" (empty string).
       • If coordinates are known, notes must be in the format: "<first>, <country>".
       • <first> must be:
           – the city in which the place is located, when the place belongs to a city;
           – the place name itself, when using a city is not appropriate for the location.
       • Both <first> and <country> must be fully translated into the target locale language inferred from locale.
       • All words in notes must be in the target locale language only. Do not keep any words in English or in any other language.

    6) Output format:
       • Return a single strictly valid JSON object with fields:
           "standardizedQuery": string,
           "resolvedName": string,
           "countryCode": string or null,
           "lat": number or null,
           "lon": number or null,
           "sourceUrls": array of strings,
           "notes": string
       • lat must be in [-90, 90] or null.
       • lon must be in [-180, 180] or null.
       • Do not invent coordinates when they cannot be reliably determined.
       • Do not add any text before or after the JSON object.

    Return only the JSON object.
    """.strip()

    try:
        resp = client.models.generate_content(
            model=model_name,
            contents=[Content(role="user", parts=[Part(text=prompt)])],
            config=GEOCODE_CFG,
        )

        candidates = getattr(resp, "candidates", None) or []
        if not candidates:
            raise ValueError("No candidates returned from model")

        parts = candidates[0].content.parts
        raw = "".join(
            getattr(p, "text", "")
            for p in parts
            if getattr(p, "text", None)
        ).strip()

        if not raw:
            raise ValueError("Empty response text from model")

        data = json.loads(raw)
        return data

    except Exception as e:
        system.logger.exception(f"geocode_with_gemini error: {e}")
        return {
            "error": f"geocoding failed: {e}",
            "input_query": place_query,
        }

