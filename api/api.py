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
'''
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


    '''

'''
# ============================================================
# Replace your /kundali route in api.py with this
# Everything (scores, yogas, doshas, dasha, D9) is now
# handled inside kundali_engine.py — no extra imports needed
# ============================================================

from astro_engine.kundali_engine import calculate_kundali

class KundaliRequest(BaseModel):
    year:   int
    month:  int
    day:    int
    hour:   int
    minute: int
    city:   str


CITIES = {
    "Pune":      (18.5204, 73.8567),
    "Mumbai":    (19.0760, 72.8777),
    "Delhi":     (28.7041, 77.1025),
    "Bangalore": (12.9716, 77.5946),
    "Chennai":   (13.0827, 80.2707),
    "Kolkata":   (22.5726, 88.3639),
    "Hyderabad": (17.3850, 78.4867),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur":    (26.9124, 75.7873),
    "Lucknow":   (26.8467, 80.9462),
}


def get_coordinates(city: str):
    """Case-insensitive city lookup with Pune as fallback."""
    for key, coords in CITIES.items():
        if key.lower() == city.strip().lower():
            return coords
    return (18.5204, 73.8567)  # default: Pune


@router.post("/kundali")
def get_kundali(data: KundaliRequest):
    lat, lon = get_coordinates(data.city)

    # calculate_kundali now returns everything:
    # planets, houses, d9_houses, panchang, dasha,
    # scores, yogas, doshas — all in one call
    return calculate_kundali(
        data.year,
        data.month,
        data.day,
        data.hour,
        data.minute,
        lat,
        lon
    )   
'''

# ================================================================
# Add these to your api.py
# ================================================================

from astro_engine.cities import CITIES, get_city
from astro_engine.kundali_engine import calculate_kundali


# ── City list endpoint (used by frontend autocomplete) ────────────
@router.get("/cities")
def get_cities():
    """Return sorted list of all supported city names."""
    return sorted(CITIES.keys())


# ── Kundali route (replaces old one) ─────────────────────────────
class KundaliRequest(BaseModel):
    year:   int
    month:  int
    day:    int
    hour:   int
    minute: int
    city:   str


@router.post("/kundali")
def get_kundali(data: KundaliRequest):
    coords = get_city(data.city)
    if coords is None:
        raise HTTPException(
            status_code=400,
            detail=f"City '{data.city}' not found. Please try a nearby major city."
        )
    lat, lon, tz = coords

    # For non-IST cities (international), adjust timezone
    # kundali_engine always expects IST input, so we compensate
    # by adjusting hour for the timezone difference
    ist_offset = 5.5
    if tz != ist_offset:
        from datetime import datetime, timedelta
        dt_local = datetime(data.year, data.month, data.day, data.hour, data.minute)
        dt_ist   = dt_local + timedelta(hours=(ist_offset - tz))
        year, month, day = dt_ist.year, dt_ist.month, dt_ist.day
        hour, minute = dt_ist.hour, dt_ist.minute
    else:
        year, month, day, hour, minute = data.year, data.month, data.day, data.hour, data.minute

    return calculate_kundali(year, month, day, hour, minute, lat, lon)

'''

from fastapi.responses import FileResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

@router.get("/download-kundali")
def download_kundali():
    global LAST_KUNDALI

    if not LAST_KUNDALI:
        return {"error": "Generate kundali first"}

    data = LAST_KUNDALI
    file_path = "kundali_report.pdf"

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(file_path)

    content = []

    # ===== TITLE =====
    content.append(Paragraph("AstroLogic Kundali Report", styles['Title']))

    # ===== BASIC DETAILS =====
    content.append(Paragraph(f"Lagna: {data['lagna']}", styles['Normal']))
    content.append(Paragraph(f"Nakshatra: {data['nakshatra']}", styles['Normal']))
    content.append(Paragraph(f"Tithi: {data['tithi_name']}", styles['Normal']))

    # ===== PLANETS =====
    content.append(Paragraph("Planetary Positions:", styles['Heading2']))

    for p in data["planets"]:
        content.append(Paragraph(
            f"{p['name']} - {p['sign']} (House {p['house']})",
            styles['Normal']
        ))

    doc.build(content)

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename="kundali_report.pdf"
    )
'''
import os
from fastapi.responses import FileResponse

@router.get("/download-kundali")
def download_kundali():
    global LAST_KUNDALI

    if not LAST_KUNDALI:
        return {"error": "Generate kundali first"}

    data = LAST_KUNDALI
    file_path = os.path.abspath("kundali_report.pdf")

    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(file_path)

    content = []

    content.append(Paragraph("AstroLogic Kundali Report", styles['Title']))
    content.append(Paragraph(f"Lagna: {data['lagna']}", styles['Normal']))

    doc.build(content)

    print("PDF CREATED AT:", file_path)

    return FileResponse(file_path, media_type="application/pdf", filename="kundali.pdf")

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

'''

# Add this import at the top of api.py
from astro_engine.festival_engine import get_festivals_range, get_upcoming_festivals, get_today_festivals
from astro_engine.horoscope_engine import generate_horoscope as generate_horoscope_direct

# Add after your existing imports (around line 200)

# ------------------ Horoscope with Index (for your HTML) ------------------
@router.get("/api/horoscope/{sign_idx}")
async def get_horoscope_by_index(sign_idx: int):
    """Get horoscope for sign index (0=Aries...11=Pisces)"""
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
    VALID_SIGNS_LIST = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                        "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    
    if sign_idx < 0 or sign_idx >= len(VALID_SIGNS_LIST):
        raise HTTPException(status_code=400, detail="Invalid sign index")
    
    sign_name = VALID_SIGNS_LIST[sign_idx]
    
    try:
        # Run in thread pool to avoid blocking
        executor = ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, generate_horoscope_direct, sign_name)
        
        # Format stars for display
        if "stars" in result:
            result["stars_display"] = {
                k: '★' * round(v) + '☆' * (5 - round(v))
                for k, v in result["stars"].items()
            }
        
        # Add planet positions for influence bars
        if "planet_details" in result:
            planet_positions = []
            for planet, details in result["planet_details"].items():
                planet_positions.append({
                    "name": planet,
                    "house": details["house"],
                    "sign": details["sign"],
                    "strength": details["strength"],
                    "retrograde": details["retrograde"],
                    "nakshatra": details["nakshatra"],
                    "domain": "various",
                    "net": 1 if details["strength"] == "Exalted" else (0.5 if details["strength"] == "Own Sign" else 0)
                })
            result["planet_positions"] = planet_positions
        
        # Add paksha if not present
        if "paksha" not in result and "tithi" in result:
            tithi_str = result["tithi"]
            result["paksha"] = "Shukla" if "Shukla" in tithi_str else ("Krishna" if "Krishna" in tithi_str else "Shukla")
        
        # Add weekday lord
        from datetime import datetime
        weekday_lords = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
        result["weekday_lord"] = weekday_lords[datetime.now().weekday()]
        
        # Add best direction if not present
        if "best_dir" not in result:
            result["best_dir"] = "East"
        
        return result
    except Exception as e:
        print(f"Error in horoscope endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ------------------ Updated Daily Horoscope Endpoint ------------------
@router.get("/daily-horoscope/{sign}")
def daily_horoscope(sign: str):
    """Get daily horoscope using local engine"""
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
    
    # Otherwise fetch new one using local engine
    print("🌍 Generating New Horoscope for", sign_lower)
    
    # Use the sync version directly for API endpoint
    try:
        sign_proper = sign_lower.capitalize()
        result = generate_horoscope_direct(sign_proper)
        
        # Add stars display
        if "stars" in result:
            result["stars_display"] = {
                k: '★' * round(v) + '☆' * (5 - round(v))
                for k, v in result["stars"].items()
            }
        
        daily_horoscope_cache["data"][sign_lower] = result
        return result
    except Exception as e:
        print(f"Error generating horoscope: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating horoscope: {str(e)}")


# ------------------ Festival Endpoints ------------------
@router.get("/api/festivals/upcoming")
async def get_upcoming_festivals_api(limit: int = 14):
    """Get upcoming festivals based on tithi calculations"""
    try:
        festivals = get_upcoming_festivals(limit)
        return {"festivals": festivals}
    except Exception as e:
        print(f"Error fetching festivals: {e}")
        return {"festivals": [], "error": str(e)}


@router.get("/api/festivals/today")
async def get_today_festivals_api():
    """Get today's festivals"""
    try:
        festivals = get_today_festivals()
        return {"festivals": festivals}
    except Exception as e:
        print(f"Error fetching today's festivals: {e}")
        return {"festivals": [], "error": str(e)}
    
'''



# ─────────────────────────────────────────────────────────────
# Horoscope & Festival Routes (festival_engine.py)
# ─────────────────────────────────────────────────────────────

from astro_engine.festival_engine import (
    generate_horoscope,
    get_today_festivals,
    get_upcoming_festivals,
)


@router.get("/horoscope/{sign_idx}")
def horoscope_by_sign(sign_idx: int):
    if not 0 <= sign_idx <= 11:
        raise HTTPException(status_code=400, detail="sign_idx must be 0-11")
    try:
        return generate_horoscope(sign_idx)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/festivals/today")
def festivals_today():
    try:
        return {"festivals": get_today_festivals()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/festivals/upcoming")
def festivals_upcoming(limit: int = 12):
    try:
        return {"festivals": get_upcoming_festivals(limit)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────
# Life Domain Analysis Route
# ─────────────────────────────────────────────────────────────
'''
from astro_engine.domain_engine import analyse_all_domains
from pydantic import BaseModel as _BM

class DomainRequest(_BM):
    year: int; month: int; day: int
    hour: int; minute: int; city: str

@router.post("/domains")
async def domains(req: DomainRequest):
    try:
        city_data = get_city(req.city)
        if not city_data:
            raise HTTPException(status_code=404, detail=f"City '{req.city}' not found")
        lat, lon, tz = city_data["lat"], city_data["lon"], city_data.get("tz", 5.5)
        from astro_engine.kundali_engine import calculate_full_kundali
        chart = calculate_full_kundali(req.year, req.month, req.day, req.hour, req.minute, lat, lon)
        return analyse_all_domains(chart)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        '''
# ============================================================
# Life Domain Analysis Route (for prediction.html)
# ============================================================

from pydantic import BaseModel as _BM
from astro_engine.domain_engine import analyse_all_domains


class DomainRequest(_BM):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    city: str

@router.post("/domains")
async def get_life_domains(req: DomainRequest):
    """10 life domain analysis for prediction.html frontend"""
    from astro_engine.domain_engine import analyse_all_domains
    from astro_engine.cities import get_city
    from astro_engine.kundali_engine import calculate_kundali
    
    # Get city coordinates - returns (lat, lon, tz) tuple
    coords = get_city(req.city)
    if coords is None:
        raise HTTPException(status_code=404, detail=f"City '{req.city}' not found")
    
    lat, lon, tz = coords  # Unpack the tuple
    
    # Calculate kundali
    chart = calculate_kundali(
        req.year, req.month, req.day, 
        req.hour, req.minute, lat, lon
    )
    
    # Analyse all domains
    result = analyse_all_domains(chart)
    
    return result


    # ─────────────────────────────────────────────────────────────────────
# KUNDALI CHAT — answers life questions from a natal chart
# ─────────────────────────────────────────────────────────────────────
import re as _re

class KundaliChatRequest(_BM):
    message: str
    chart: dict   # full kundali output from /api/kundali

DASHA_YRS = dict(Ketu=7,Venus=20,Sun=6,Moon=10,Mars=7,Rahu=18,Jupiter=16,Saturn=19,Mercury=17)
DASHA_SEQ = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
SIGN_LORDS_MAP = {
    "Mesha":"Mars","Vrishabha":"Venus","Mithuna":"Mercury","Karka":"Moon",
    "Simha":"Sun","Kanya":"Mercury","Tula":"Venus","Vrischika":"Mars",
    "Dhanu":"Jupiter","Makara":"Saturn","Kumbha":"Saturn","Meena":"Jupiter"
}
RASHI = ["Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya",
         "Tula","Vrischika","Dhanu","Makara","Kumbha","Meena"]
EXALT = dict(Sun="Mesha",Moon="Vrishabha",Mars="Makara",Mercury="Kanya",
             Jupiter="Karka",Venus="Meena",Saturn="Tula")
DEBIL = dict(Sun="Tula",Moon="Vrischika",Mars="Karka",Mercury="Meena",
             Jupiter="Makara",Venus="Kanya",Saturn="Mesha")

def _pmap(chart):
    pm = {}
    for p in chart.get("planets",[]):
        pm[p["name"]] = p
    return pm

def _house_of(pm, name):
    p = pm.get(name,{})
    h = p.get("house",0)
    if isinstance(h,int): return h
    try: return int(str(h).split("/")[0])
    except: return 0

def _sign_of(pm, name):
    return pm.get(name,{}).get("sign","")

def _pstr(pm, name):
    p = pm.get(name,{})
    sign = p.get("sign",""); house = _house_of(pm, name)
    st = p.get("strength","")
    retro = " (R)" if p.get("retrograde") else ""
    return f"{name} in {sign} (H{house}){retro} — {st}"

def _lord_of_house(lagna_sign, house_no):
    lagna_idx = RASHI.index(lagna_sign) if lagna_sign in RASHI else 0
    sign = RASHI[(lagna_idx + house_no - 1) % 12]
    return SIGN_LORDS_MAP[sign], sign

def _dasha_timeline(mahadasha, balance_str, birth_year):
    """Build full mahadasha timeline from birth."""
    try:
        balance = float(str(balance_str).replace(" years",""))
    except:
        balance = 5.0
    md_idx = DASHA_SEQ.index(mahadasha)
    years_spent = DASHA_YRS[mahadasha] - balance
    md_start_year = birth_year - years_spent
    timeline = []
    cursor = md_start_year
    for i in range(9):
        lord = DASHA_SEQ[(md_idx + i) % 9]
        yrs  = DASHA_YRS[lord] if i > 0 else balance
        if i == 0: yrs = balance
        else: yrs = DASHA_YRS[lord]
        end = cursor + yrs
        timeline.append({"lord":lord,"start":round(cursor,1),"end":round(end,1),"years":round(yrs,1)})
        cursor = end
    return timeline

def _answer_career_question(pm, chart, birth_year):
    lagna = chart.get("lagna","")
    lord_10, sign_10 = _lord_of_house(lagna, 10)
    l10_house = _house_of(pm, lord_10)
    l10_sign  = _sign_of(pm, lord_10)
    l10_str   = pm.get(lord_10,{}).get("strength","Neutral")
    h10_planets = [p for p,d in pm.items() if _house_of(pm,p)==10]
    md = chart.get("mahadasha","")
    ad = chart.get("antardasha","")
    bal = chart.get("dasha_balance","")
    try: bal_f = float(str(bal).replace(" years",""))
    except: bal_f = 5
    md_end_year = birth_year + bal_f

    # Career timing
    tl = _dasha_timeline(md, bal, birth_year)
    career_dashas = []
    for t in tl:
        lord = t["lord"]
        l_house = _house_of(pm, lord)
        lords_house_no = None
        for h in range(1,13):
            lh, _ = _lord_of_house(lagna, h)
            if lh == lord and h in (10,6,11):
                lords_house_no = h
        if l_house in (10,6,11) or lords_house_no:
            career_dashas.append(t)

    parts = []
    parts.append(f"**10th house** (career) falls in **{sign_10}**, ruled by **{lord_10}**.")
    parts.append(f"{lord_10} is placed in {l10_sign} in the {_ord(l10_house)} house — {l10_str}.")
    if h10_planets:
        parts.append(f"Planets in 10th house: **{', '.join(h10_planets)}** — these shape your professional field and style.")
    # Current dasha
    parts.append(f"\nCurrent **{md}/{ad}** dasha (balance: {bal}).")
    l_of_md = _house_of(pm, md)
    if l_of_md in (10,6,11) or any(_lord_of_house(lagna,h)[0]==md for h in (10,6,11)):
        parts.append(f"✅ **{md}** Mahadasha is career-activating — this is a strong period for professional growth.")
    else:
        parts.append(f"**{md}** Mahadasha does not directly trigger career houses. Focus on foundations now.")
    if career_dashas:
        best = career_dashas[0]
        parts.append(f"\n🎯 **Best career period**: {best['lord']} Mahadasha (~{int(best['start'])}–{int(best['end'])}) — career houses activated.")
    return "\n".join(parts)

def _answer_marriage_question(pm, chart, birth_year):
    lagna = chart.get("lagna","")
    lord_7, sign_7 = _lord_of_house(lagna, 7)
    l7_house = _house_of(pm, lord_7)
    l7_str   = pm.get(lord_7,{}).get("strength","Neutral")
    h7_pl    = [p for p,d in pm.items() if _house_of(pm,p)==7]
    venus    = pm.get("Venus",{}); venus_h = _house_of(pm,"Venus")
    mars_h   = _house_of(pm,"Mars")
    md = chart.get("mahadasha",""); bal = chart.get("dasha_balance","")
    try: bal_f = float(str(bal).replace(" years",""))
    except: bal_f = 5
    tl = _dasha_timeline(md, bal, birth_year)
    marriage_dashas = []
    for t in tl:
        lord = t["lord"]
        l_house = _house_of(pm, lord)
        if l_house in (7,5,2) or any(_lord_of_house(lagna,h)[0]==lord for h in (7,5,2)):
            marriage_dashas.append(t)
    mangal = mars_h in (1,2,4,7,8,12)
    parts = []
    parts.append(f"**7th house** (marriage) in **{sign_7}**, ruled by **{lord_7}** (in {_ord(l7_house)}H — {l7_str}).")
    if h7_pl: parts.append(f"Planets in 7th: **{', '.join(h7_pl)}** — shape partner's qualities.")
    parts.append(f"**Venus** (marriage karaka) in {venus.get('sign','')} H{venus_h} — {venus.get('strength','Neutral')}.")
    if mangal:
        mars_sign = _sign_of(pm,"Mars")
        cancelled = mars_sign in ("Makara","Mesha","Vrischika")
        parts.append(f"⚠️ **Mangal Dosh** — Mars in {mars_h}th house.{'Cancelled — Mars is strong.' if cancelled else ' Consider matching with similar chart pattern.'}")
    if marriage_dashas:
        best = marriage_dashas[0]
        parts.append(f"\n🎯 **Marriage timing**: {best['lord']} Mahadasha (~{int(best['start'])}–{int(best['end'])}) activates relationship houses.")
    return "\n".join(parts)

def _answer_wealth_question(pm, chart, birth_year):
    lagna = chart.get("lagna","")
    lord_2, s2 = _lord_of_house(lagna, 2); lord_11, s11 = _lord_of_house(lagna, 11)
    l2_h = _house_of(pm, lord_2); l11_h = _house_of(pm, lord_11)
    jup   = pm.get("Jupiter",{}); jup_h = _house_of(pm,"Jupiter")
    md = chart.get("mahadasha",""); bal = chart.get("dasha_balance","")
    try: bal_f = float(str(bal).replace(" years",""))
    except: bal_f = 5
    tl = _dasha_timeline(md, bal, birth_year)
    wealth_dashas = [t for t in tl if _house_of(pm,t["lord"]) in (2,11,9) or any(_lord_of_house(lagna,h)[0]==t["lord"] for h in (2,11))]
    parts = []
    parts.append(f"**2nd lord** {lord_2} in {_ord(l2_h)}H; **11th lord** {lord_11} in {_ord(l11_h)}H.")
    parts.append(f"**Jupiter** (wealth karaka) in {jup.get('sign','')} H{jup_h} — {jup.get('strength','Neutral')}.")
    if wealth_dashas:
        best = wealth_dashas[0]
        parts.append(f"\n🎯 **Wealth peak**: {best['lord']} Mahadasha (~{int(best['start'])}–{int(best['end'])}).")
    return "\n".join(parts)

def _answer_health_question(pm, chart, birth_year):
    lagna = chart.get("lagna","")
    lord_1, _ = _lord_of_house(lagna, 1)
    l1_h = _house_of(pm, lord_1); l1_str = pm.get(lord_1,{}).get("strength","")
    sun = pm.get("Sun",{}); moon = pm.get("Moon",{})
    h6_pl = [p for p,d in pm.items() if _house_of(pm,p)==6]
    h8_pl = [p for p,d in pm.items() if _house_of(pm,p)==8]
    AYUR = {"Mesha":"Pitta","Vrishabha":"Kapha","Mithuna":"Vata","Karka":"Kapha",
            "Simha":"Pitta","Kanya":"Vata","Tula":"Vata","Vrischika":"Pitta",
            "Dhanu":"Pitta","Makara":"Vata","Kumbha":"Vata","Meena":"Kapha"}
    parts = []
    parts.append(f"**Lagna lord** {lord_1} in {_ord(l1_h)}H — {l1_str} (determines vitality).")
    parts.append(f"Ayurvedic Prakriti ({lagna} lagna): **{AYUR.get(lagna,'Tridoshic')}**.")
    parts.append(f"Sun H{_house_of(pm,'Sun')} {sun.get('strength','')}, Moon H{_house_of(pm,'Moon')} {moon.get('strength','')}.")
    if h6_pl: parts.append(f"6th house (disease): {', '.join(h6_pl)} — watch health in {', '.join(h6_pl)} Dasha.")
    if h8_pl: parts.append(f"8th house: {', '.join(h8_pl)} — surgery/transformation potential.")
    return "\n".join(parts)

def _answer_foreign_question(pm, chart, birth_year):
    lagna = chart.get("lagna","")
    lord_12, s12 = _lord_of_house(lagna, 12); lord_9, s9 = _lord_of_house(lagna, 9)
    rahu_h = _house_of(pm,"Rahu"); l12_h = _house_of(pm, lord_12)
    h12_pl = [p for p,d in pm.items() if _house_of(pm,p)==12]
    md = chart.get("mahadasha",""); bal = chart.get("dasha_balance","")
    try: bal_f = float(str(bal).replace(" years",""))
    except: bal_f = 5
    tl = _dasha_timeline(md, bal, birth_year)
    foreign_strong = rahu_h in (1,7,9,12) or "Rahu" in h12_pl
    foreign_dashas = [t for t in tl if _house_of(pm,t["lord"]) in (12,9) or t["lord"]=="Rahu"]
    parts = []
    parts.append(f"**12th house** (foreign): ruled by {lord_12} in {_ord(l12_h)}H.")
    parts.append(f"**Rahu** in {_ord(rahu_h)}H — {'Strong foreign indicator' if foreign_strong else 'Foreign travel possible but not dominant'}.")
    if foreign_dashas:
        best = foreign_dashas[0]
        parts.append(f"🎯 **Foreign opportunity**: ~{int(best['start'])}–{int(best['end'])} ({best['lord']} Mahadasha).")
    return "\n".join(parts)

def _answer_children_question(pm, chart, birth_year):
    lagna = chart.get("lagna","")
    lord_5, s5 = _lord_of_house(lagna, 5)
    l5_h = _house_of(pm, lord_5); jup_h = _house_of(pm,"Jupiter")
    jup_str = pm.get("Jupiter",{}).get("strength",""); jup_sign = _sign_of(pm,"Jupiter")
    h5_pl = [p for p,d in pm.items() if _house_of(pm,p)==5]
    md = chart.get("mahadasha",""); bal = chart.get("dasha_balance","")
    try: bal_f = float(str(bal).replace(" years",""))
    except: bal_f = 5
    tl = _dasha_timeline(md, bal, birth_year)
    child_dashas = [t for t in tl if _house_of(pm,t["lord"]) in (5,9) or t["lord"] in ("Jupiter","Moon")]
    parts = []
    parts.append(f"**5th house** (children): {s5}, ruled by {lord_5} in {_ord(l5_h)}H.")
    parts.append(f"**Jupiter** (putra karaka) in {jup_sign} H{jup_h} — {jup_str}.")
    if h5_pl: parts.append(f"Planets in 5th: {', '.join(h5_pl)}.")
    if child_dashas:
        best = child_dashas[0]
        parts.append(f"🎯 **Childbirth timing**: {best['lord']} Dasha (~{int(best['start'])}–{int(best['end'])}).")
    return "\n".join(parts)

def _answer_education_question(pm, chart, birth_year):
    lagna = chart.get("lagna","")
    lord_4, _ = _lord_of_house(lagna, 4); lord_5, _ = _lord_of_house(lagna, 5)
    merc = pm.get("Mercury",{}); jup = pm.get("Jupiter",{})
    parts = []
    parts.append(f"**Mercury** (intellect) in {merc.get('sign','')} H{_house_of(pm,'Mercury')} — {merc.get('strength','')}.")
    parts.append(f"**Jupiter** (wisdom) in {jup.get('sign','')} H{_house_of(pm,'Jupiter')} — {jup.get('strength','')}.")
    rahu_h = _house_of(pm,"Rahu")
    if rahu_h in (4,5,9): parts.append("Rahu in education house — foreign education strongly indicated.")
    return "\n".join(parts)

def _ord(n):
    s = {1:"st",2:"nd",3:"rd"}.get(n if n<20 else n%10,"th")
    return f"{n}{s}"

def _detect_topic(msg):
    msg = msg.lower()
    if any(w in msg for w in ["job","career","profession","work","business","promotion","salary","office"]): return "career"
    if any(w in msg for w in ["marr","husband","wife","spouse","partner","love","relat","wedding","engagement"]): return "marriage"
    if any(w in msg for w in ["wealth","money","rich","income","finance","earn","invest","profit","loss","debt"]): return "wealth"
    if any(w in msg for w in ["health","sick","disease","illness","hospital","surgery","medicine","body","organ"]): return "health"
    if any(w in msg for w in ["foreign","abroad","visa","immigr","settle","overseas","travel","country","usa","uk","canada"]): return "foreign"
    if any(w in msg for w in ["child","son","daughter","baby","pregnan","putra","kid","conceive","birth"]): return "children"
    if any(w in msg for w in ["study","educat","school","college","exam","degree","learn","course","university"]): return "education"
    if any(w in msg for w in ["property","house","home","land","flat","plot","real estate","vastu"]): return "property"
    if any(w in msg for w in ["spiritual","karma","moksha","dharma","religion","god","devotion","mantra","meditation"]): return "spirituality"
    if any(w in msg for w in ["dasha","antardasha","period","mahadasha","when","timing","year","time"]): return "timing"
    if any(w in msg for w in ["yoga","raj yoga","dhana","gajakesari","budhaditya"]): return "yoga"
    if any(w in msg for w in ["dosha","mangal","sade","kaal sarp","pitru","grahan","dosh"]): return "dosha"
    if any(w in msg for w in ["lagna","ascendant","rising","chart","house","planet","sign","rashi"]): return "chart"
    if any(w in msg for w in ["remedy","gemstone","mantra","puja","fast","donate","wear","ring","stone"]): return "remedy"
    return "general"

@router.post("/kundali-chat")
async def kundali_chat(data: KundaliChatRequest):
    """Smart kundali-aware chat — answers life questions from natal chart."""
    chart = data.chart
    msg   = data.message.strip()

    if not chart:
        return {"reply":"Please generate your Kundali first, then ask your question.","topic":"error"}

    pm     = _pmap(chart)
    lagna  = chart.get("lagna","")
    md     = chart.get("mahadasha","")
    ad     = chart.get("antardasha","")
    bal    = chart.get("dasha_balance","")
    yogas  = [y.get("name","") for y in chart.get("yogas",[]) if y.get("present")]
    doshas = [d.get("name","") for d in chart.get("doshas",[]) if d.get("present")]

    # Estimate birth year from dasha balance (approximate)
    try:
        bal_f = float(str(bal).replace(" years",""))
    except:
        bal_f = 5.0
    from datetime import datetime
    current_year = datetime.now().year
    birth_year_approx = current_year - (DASHA_YRS.get(md, 10) - bal_f)

    topic = _detect_topic(msg)

    # Build topic-specific answer
    if topic == "career":
        core = _answer_career_question(pm, chart, birth_year_approx)
    elif topic == "marriage":
        core = _answer_marriage_question(pm, chart, birth_year_approx)
    elif topic == "wealth":
        core = _answer_wealth_question(pm, chart, birth_year_approx)
    elif topic == "health":
        core = _answer_health_question(pm, chart, birth_year_approx)
    elif topic == "foreign":
        core = _answer_foreign_question(pm, chart, birth_year_approx)
    elif topic == "children":
        core = _answer_children_question(pm, chart, birth_year_approx)
    elif topic == "education":
        core = _answer_education_question(pm, chart, birth_year_approx)
    elif topic == "dosha":
        core = f"**Active Doshas**: {', '.join(doshas) if doshas else 'None detected'}\n" + \
               f"**Active Yogas**: {', '.join(yogas[:4]) if yogas else 'None detected'}"
    elif topic == "yoga":
        core = f"**Active Yogas in your chart**: {', '.join(yogas) if yogas else 'None detected'}\n" + \
               f"Yogas become fully active during the relevant planet's Mahadasha."
    elif topic == "timing":
        tl = _dasha_timeline(md, bal, birth_year_approx)
        core = f"**Current Dasha**: {md}/{ad} (balance: {bal})\n\n**Upcoming Mahadasha timeline:**\n" + \
               "\n".join([f"• {t['lord']}: ~{int(t['start'])}–{int(t['end'])} ({t['years']}y)" for t in tl[:6]])
    elif topic == "remedy":
        GEMS = dict(Sun="Ruby",Moon="Pearl",Mars="Red Coral",Mercury="Emerald",
                    Jupiter="Yellow Sapphire",Venus="Diamond/White Sapphire",Saturn="Blue Sapphire",
                    Rahu="Hessonite",Ketu="Cat's Eye")
        weak = [(p,d) for p,d in pm.items() if "Debilitated" in d.get("strength","")]
        if weak:
            core = "**Weak planets needing support:**\n" + \
                   "\n".join([f"• **{p}** (Debilitated in {d.get('sign','')}): Gemstone — {GEMS.get(p,'consult astrologer')}, fast on {dict(Sun='Sunday',Moon='Monday',Mars='Tuesday',Mercury='Wednesday',Jupiter='Thursday',Venus='Friday',Saturn='Saturday',Rahu='Saturday',Ketu='Tuesday').get(p,'')}" for p,d in weak[:3]])
        else:
            core = f"No severely debilitated planets. Current {md} Mahadasha — consider strengthening {md}: {GEMS.get(md,'consult astrologer')}."
    else:
        # General: give overview
        core = f"**Your Chart Summary**\n" + \
               f"Lagna: **{lagna}** | Mahadasha: **{md}/{ad}** (balance: {bal})\n" + \
               f"Active Yogas: {', '.join(yogas[:3]) if yogas else 'None'}\n" + \
               f"Active Doshas: {', '.join(doshas[:3]) if doshas else 'None'}\n\n" + \
               f"Please ask a specific question about career, marriage, wealth, health, foreign travel, children, education, or timing for a detailed answer."

    return {
        "reply": core,
        "topic": topic,
        "chart_context": {
            "lagna": lagna,
            "mahadasha": md,
            "antardasha": ad,
            "dasha_balance": bal,
            "active_yogas": yogas[:5],
            "active_doshas": doshas[:3],
        }
    }