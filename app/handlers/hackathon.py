# -*- coding: utf-8 -*-

from typing import Dict, Any, Optional
from fastapi import HTTPException
from fastapi import APIRouter
from pydantic import BaseModel

from modules.genai import extract_full_profile, geocode_with_gemini, UserProfile, update_profile_from_text
from enum import Enum

class LLMBackend(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"


router = APIRouter(
    prefix="/profile",
    tags=["profile"],
)

router.app = "api"

class ProfileExtractRequest(BaseModel):
    text: str
    locale: str = "en"
    returnValues: bool = False
    backend: LLMBackend = LLMBackend.GEMINI
    currentState: Optional[UserProfile] = None

class ProfileExtractResponse(BaseModel):
    profile: UserProfile

class GeocodeRequest(BaseModel):
    query: str
    locale: str = "en"

class GeocodeResponse(BaseModel):
    standardizedQuery: str = ""
    resolvedName: str = ""
    countryCode: str | None = None
    lat: float | None = None
    lon: float | None = None
    sourceUrls: list[str] = []
    notes: str = ""


@router.post(
    "/extract",
    response_model=ProfileExtractResponse,
    summary="Update user profile from free text",
)
async def extract_profile(payload: ProfileExtractRequest) -> ProfileExtractResponse:
    state = payload.currentState or UserProfile()

    new_state, _ = update_profile_from_text(
        text=payload.text,
        locale=payload.locale,
        state=state,
        return_values=payload.returnValues,
    )

    return ProfileExtractResponse(profile=new_state)


@router.post(
    "/geocode",
    response_model=GeocodeResponse,
    summary="Geocode place with Gemini",
)
async def geocode_place(payload: GeocodeRequest) -> GeocodeResponse:
    raw = geocode_with_gemini(payload.query, locale=payload.locale)


    if isinstance(raw, dict) and "error" in raw:
        raise HTTPException(status_code=400, detail=raw["error"])

    return GeocodeResponse(
        standardizedQuery=raw.get("standardizedQuery", ""),
        resolvedName=raw.get("resolvedName", ""),
        countryCode=raw.get("countryCode"),
        lat=raw.get("lat"),
        lon=raw.get("lon"),
        sourceUrls=raw.get("sourceUrls", []),
        notes=raw.get("notes"),
    )
