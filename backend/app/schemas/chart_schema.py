# api/schemas/chart_schemas.py

from pydantic import BaseModel
from typing import Dict, List, Optional


# ============================
# INPUT SCHEMA
# ============================

class BirthData(BaseModel):
    name: Optional[str] = "Seeker"
    year: int
    month: int
    day: int
    hour: float
    place: Optional[str] = "Unknown"


# ============================
# PLANET STRUCTURE
# ============================

class PlanetDetails(BaseModel):
    planet: str
    degree: float
    sign: str
    navamsa: str
    nakshatra: str
    pada: int
    bhava_house: int
    strength: str


# ============================
# DASHA STRUCTURE
# ============================

class DashaTimeline(BaseModel):
    lord: str
    years: float


class DashaDetails(BaseModel):
    current_mahadasha: str
    balance_years: float
    timeline: List[DashaTimeline]


# ============================
# EVENT PREDICTION STRUCTURE
# ============================

class EventPrediction(BaseModel):
    event: str
    score: float
    confidence: float
    level: str
    reasons: List[str]


# ============================
# FULL CHART RESPONSE
# ============================

class ChartResponse(BaseModel):
    basic_details: Dict
    planets_by_house: Dict[str, List[PlanetDetails]]
    house_lords: Dict
    dasha: DashaDetails
    activated_houses: List[int]
    functional_nature: Dict
    dispositors: Dict
    vedic_aspects: Dict
    current_transits: Dict
    advanced_yogas: List[str]
    planet_strength_scores: Dict[str, float]
    marriage_prediction: EventPrediction
    career_prediction: EventPrediction
    marriage_explanation: str
    career_explanation: str