"""
api/horoscope_routes.py
New routes for:
  GET  /api/festivals/today      — today's tithi-based festivals
  GET  /api/festivals/upcoming   — next 12 festivals
  GET  /api/horoscope/{sign_idx} — dynamic horoscope for sign 0-11
"""

from fastapi import APIRouter
from astro_engine.festival_engine import (
    get_today_festivals,
    get_upcoming_festivals,
    generate_horoscope,
)

router = APIRouter(prefix="/api", tags=["Horoscope & Festivals"])


@router.get("/festivals/today")
def festivals_today():
    return {"festivals": get_today_festivals()}


@router.get("/festivals/upcoming")
def festivals_upcoming(limit: int = 12):
    return {"festivals": get_upcoming_festivals(limit)}


@router.get("/horoscope/{sign_idx}")
def horoscope(sign_idx: int):
    if not 0 <= sign_idx <= 11:
        return {"error": "sign_idx must be 0-11 (0=Aries … 11=Pisces)"}
    return generate_horoscope(sign_idx)