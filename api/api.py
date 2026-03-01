from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import swisseph as swe
import json
from datetime import date


from .schemas.chart_schemas import BirthData
from astro_engine.panchang_engine import get_full_panchang
from astro_engine.kundali_engine import calculate_kundali
from astro_engine.planets import calculate_all_planets
from astro_engine.zodiac import degree_to_sign
from astro_engine.houses import calculate_lagna
from astro_engine.chart_engine import generate_full_chart
from astro_engine.llm_engine import ask_llm
from astro_engine.prediction_builder import build_prediction_prompt
from services.horoscope_service import fetch_horoscope
from astro_engine.scoring import calculate_chart_scores

router = APIRouter(prefix="/api", tags=["API"])

# ------------ Panchang --------------

class PanchangRequest(BaseModel):
    city: str

@router.post("/panchang")
def panchang_city(request: PanchangRequest):
    return get_full_panchang(request.city)

# ------------------ Generate Chart ------------------

@router.post("/generate-chart")
def generate_chart_api(data: BirthData):

    jd = swe.julday(data.year, data.month, data.day, data.hour)

    planets = calculate_all_planets(jd)

    lagna_degree = calculate_lagna(jd)
    lagna_sign = degree_to_sign(lagna_degree)

    return {
        "basic_details": {
            "date": f"{data.day}-{data.month}-{data.year}",
            "time": data.hour,
            "lagna": lagna_sign
        },
        "planets": planets
    }

# ------------- Kundali ------------

class KundaliRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    city: str


def get_coordinates(city):
    cities = {
        "Pune": (18.5204, 73.8567),
        "Mumbai": (19.0760, 72.8777),
        "Delhi": (28.7041, 77.1025)
    }
    return cities.get(city, (18.5204, 73.8567))


@router.post("/kundali")
def get_kundali(data: KundaliRequest):

    lat, lon = get_coordinates(data.city)

    return calculate_kundali(
        data.year,
        data.month,
        data.day,
        data.hour,
        data.minute,
        lat,
        lon
    )

    # 🔹 Convert chart into planets_by_house structure
    planets_by_house = {}

    for planet, details in chart_data.get("planets", {}).items():
        house = details.get("house")
        strength = details.get("strength", "")

        if house not in planets_by_house:
            planets_by_house[house] = []

        planets_by_house[house].append({
            "planet": planet,
            "strength": strength
        })

        chart_data["planets_by_house"] = planets_by_house

    # 🔹 STEP 2: Safely Calculate Scores
    try:
        scores = calculate_chart_scores(chart_data)
        

    except Exception as e:
        print("Scoring error:", e)
        scores = {
            "overall_strength": 0,
            "marriage_score": 0,
            "career_score": 0,
            "finance_score": 0,
            "mental_score": 0
        }
    
    # 🔹 STEP 3: Return Combined Response
    return {
        "birth_details": {
            "year": data.year,
            "month": data.month,
            "day": data.day,
            "hour": data.hour,
            "minute": data.minute,
            "city": data.city
        },
        "chart": chart_data,
        "scores": scores
    }
# ------------------ Daily Horoscope ------------------

from services.horoscope_service import fetch_horoscope
from fastapi import HTTPException

# ✅ GLOBAL VARIABLE HERE
daily_horoscope_cache = {
    "date": None,
    "data": {}
}
VALID_SIGNS = [
    "aries","taurus","gemini","cancer","leo","virgo",
    "libra","scorpio","sagittarius","capricorn","aquarius","pisces"
]

@router.get("/daily-horoscope/{sign}")
def daily_horoscope(sign: str):

    global daily_horoscope_cache

    sign_lower = sign.lower()

    if sign_lower not in VALID_SIGNS:
        raise HTTPException(status_code=400, detail="Invalid zodiac sign")

    today = str(date.today())

    # Reset cache if new day
    if daily_horoscope_cache["date"] != today:
        print("🆕 New Day — Resetting Horoscope Cache")
        daily_horoscope_cache["date"] = today
        daily_horoscope_cache["data"] = {}

    # Return cached value if exists
    if sign_lower in daily_horoscope_cache["data"]:
        print("⚡ Returning Cached Horoscope for", sign_lower)
        return daily_horoscope_cache["data"][sign_lower]

    # Otherwise fetch new one
    print("🌍 Fetching New Horoscope for", sign_lower)

    result = fetch_horoscope(sign_lower)

    daily_horoscope_cache["data"][sign_lower] = result

    return result

    #----------------- Predictions ----------------------
# ------------------------------
# In-memory storage for last chart
# ------------------------------
last_generated_chart = None


# ------------------------------
# Prediction Request Model
# ------------------------------
class PredictionRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: float


# ------------------------------
# Chat Request Model
# ------------------------------
class ChatRequest(BaseModel):
    message: str


# ==================================================
# 🔮 PREDICTION MODULE
# ==================================================
@router.post("/prediction")
def generate_prediction(data: PredictionRequest):

    global last_generated_chart

    print("\n========== PREDICTION REQUEST ==========")
    print("INPUT:", data)

    latitude = 18.5204
    longitude = 73.8567

    print("[1/3] Generating Chart...")
    chart = generate_full_chart(
        data.year,
        data.month,
        data.day,
        data.hour,
        latitude,
        longitude
    )

    # Save chart globally for chat use
    last_generated_chart = chart

    with open("last_chart.json", "w") as f:
        json.dump(chart, f, indent=4, default=str)

    print("[2/3] AI Marriage Analysis...")
    marriage_prompt = build_prediction_prompt(chart, "marriage")
    marriage_output = ask_llm(marriage_prompt)

    print("[3/3] AI Career Analysis...")
    career_prompt = build_prediction_prompt(chart, "career")
    career_output = ask_llm(career_prompt)

    print("========== COMPLETE ==========\n")

    return {
        "marriage_prediction": marriage_output,
        "career_prediction": career_output
    }


# ==================================================
# 💬 CHAT MODULE (Uses Last Generated Chart)
# ==================================================
@router.post("/chat")
def astro_chat(data: ChatRequest):

    global last_generated_chart

    print("\n========= CHAT REQUEST =========")
    print("USER:", data.message)

    if last_generated_chart is None:
        return {
            "reply": "Please generate prediction first before using chat."
        }

    # Build contextual prompt
    chat_prompt = f"""
You are AstroAI, a professional Vedic astrologer.

Use the following birth chart context to answer.

Chart Summary:
{json.dumps(last_generated_chart, indent=2)}

User Question:
{data.message}

Give structured and clear astrological explanation.
Keep answer under 120 words.
"""

    ai_response = ask_llm(chat_prompt)

    print("AI:", ai_response)
    print("================================\n")

    return {"reply": ai_response}

    # ------------------ Blogs ------------------

from database import SessionLocal
from models.blog_model import Blog
from sqlalchemy.orm import Session
from fastapi import Depends


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------ Create Blog ------------------



# ------------------ Get All Blogs ------------------

@router.get("/blogs")
def get_blogs(db: Session = Depends(get_db)):
    blogs = db.query(Blog).order_by(Blog.id.desc()).all()
    return blogs


# ------------------ Get Single Blog ------------------

@router.get("/blogs/{blog_id}")
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        return {"error": "Blog not found"}

    return blog
#---------------- admin blog -----------------
from fastapi import Form

@router.post("/blogs")
def create_blog(
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    blog = Blog(title=title, content=content)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return {"message": "Blog created successfully"}