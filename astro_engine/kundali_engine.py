'''
import swisseph as swe
from datetime import datetime

swe.set_sid_mode(swe.SIDM_LAHIRI)
IST_OFFSET = 5.5

RASHI_NAMES = [
"Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya",
"Tula","Vrischika","Dhanu","Makara","Kumbha","Meena"
]

PLANETS = [
("Sun", swe.SUN),
("Moon", swe.MOON),
("Mercury", swe.MERCURY),
("Venus", swe.VENUS),
("Mars", swe.MARS),
("Jupiter", swe.JUPITER),
("Saturn", swe.SATURN),
("Rahu", swe.MEAN_NODE),
("Ketu", swe.TRUE_NODE)
]


def calculate_kundali(year, month, day, hour, minute, lat, lon):

    # Convert to UT
    jd = swe.julday(year, month, day,
                    hour + minute/60 - IST_OFFSET)

    # Calculate Lagna
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    lagna_degree = ascmc[0]

    lagna_sign_index = int(lagna_degree / 30)
    lagna_sign = RASHI_NAMES[lagna_sign_index]

    # Create 12 houses dictionary
    houses = {i: [] for i in range(1, 13)}

    # Add Lagna
    houses[1].append("Lagna")

    planet_data = []

    for name, p in PLANETS:

        data = swe.calc_ut(jd, p, swe.FLG_SIDEREAL | swe.FLG_SPEED)
        lon_planet = data[0][0]
        speed = data[0][3]

        sign_index = int(lon_planet / 30)
        sign_name = RASHI_NAMES[sign_index]

        # House calculation
        house_number = ((sign_index - lagna_sign_index) % 12) + 1
        houses[house_number].append(name)

        planet_data.append({
            "name": name,
            "sign": sign_name,
            "degree": round(lon_planet % 30, 2),
            "house": house_number,
            "retrograde": speed < 0
        })

    return {
        "lagna": lagna_sign,
        "lagna_degree": round(lagna_degree % 30, 2),
        "houses": houses,
        "planets": planet_data
    }
    '''

#========================================================================

'''
import swisseph as swe
from datetime import datetime
from datetime import datetime, timezone, timedelta


# Set Lahiri Ayanamsa
swe.set_sid_mode(swe.SIDM_LAHIRI)

IST_OFFSET = 5.5

# 12 Zodiac Signs
RASHI_NAMES = [
    "Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya",
    "Tula","Vrischika","Dhanu","Makara","Kumbha","Meena"
]

# 27 Nakshatras
NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
    "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha",
    "Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha",
    "Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
    "Uttara Bhadrapada","Revati"
]

# 30 Tithi Names
TITHI_NAMES = [
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami",
    "Shashthi","Saptami","Ashtami","Navami","Dashami",
    "Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Purnima/Amavasya"
]

PLANETS = [
    ("Sun", swe.SUN),
    ("Moon", swe.MOON),
    ("Mercury", swe.MERCURY),
    ("Venus", swe.VENUS),
    ("Mars", swe.MARS),
    ("Jupiter", swe.JUPITER),
    ("Saturn", swe.SATURN),
    ("Rahu", swe.TRUE_NODE)
]

def calculate_kundali(year, month, day, hour, minute, lat, lon):

    # Convert to UT
    #jd = swe.julday(year, month, day,
    #                hour + minute/60 - IST_OFFSET)

    # Convert IST → UTC properly
    dt_ist = datetime(year, month, day, hour, minute)
    dt_utc = dt_ist - timedelta(hours=5, minutes=30)

    jd = swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600
    )

    # Calculate Lagna
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    lagna_degree = ascmc[0]
    lagna_sign_index = int(lagna_degree / 30)
    lagna_sign = RASHI_NAMES[lagna_sign_index]

    # Create 12 houses dictionary
    houses = {i: [] for i in range(1, 13)}
    houses[1].append("Lagna")

    planet_data = []

    for name, p in PLANETS:
        #data = swe.calc_ut(jd, p, swe.FLG_SIDEREAL | swe.FLG_SPEED)
        FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

        data = swe.calc_ut(jd, p, FLAGS)
        
        lon_planet = data[0][0]
        speed = data[0][3]

        sign_index = int(lon_planet / 30)
        sign_name = RASHI_NAMES[sign_index]

        house_number = ((sign_index - lagna_sign_index) % 12) + 1
        houses[house_number].append(name)

        planet_data.append({
            "name": name,
            "sign": sign_name,
            "degree": round(lon_planet % 30, 2),
            "house": house_number,
            "retrograde": speed < 0
        })

    # ---- Add Ketu manually (180° from Rahu) ----
    rahu = next(p for p in planet_data if p["name"] == "Rahu")
    rahu_full = (RASHI_NAMES.index(rahu["sign"]) * 30) + rahu["degree"]
    ketu_full = (rahu_full + 180) % 360

    ketu_sign_index = int(ketu_full / 30)
    ketu_sign = RASHI_NAMES[ketu_sign_index]
    ketu_house = ((ketu_sign_index - lagna_sign_index) % 12) + 1

    houses[ketu_house].append("Ketu")

    planet_data.append({
        "name": "Ketu",
        "sign": ketu_sign,
        "degree": round(ketu_full % 30, 2),
        "house": ketu_house,
        "retrograde": True
    })

    # ---- Panchang Calculations ----

    sun = next(p for p in planet_data if p["name"] == "Sun")
    moon = next(p for p in planet_data if p["name"] == "Moon")

    sun_full = (RASHI_NAMES.index(sun["sign"]) * 30) + sun["degree"]
    moon_full = (RASHI_NAMES.index(moon["sign"]) * 30) + moon["degree"]

    # ---- Tithi ----
    tithi_calc = ((moon_full - sun_full) % 360) / 12
    tithi_number = int(tithi_calc) + 1
    tithi_name = TITHI_NAMES[(tithi_number - 1) % 15]

    # ---- Nakshatra ----
    nak_index = int(moon_full / 13.3333)
    nakshatra = NAKSHATRAS[nak_index]

    # ---- Yoga ----
    yoga_degree = (sun_full + moon_full) % 360
    yoga_number = int(yoga_degree / 13.3333) + 1

    # ---- Karana ----
    karana_number = int(((moon_full - sun_full) % 360) / 6) + 1

    # ---- Ayanamsa ----
    ayanamsa = swe.get_ayanamsa(jd)

    return {
    "lagna": lagna_sign,
    "lagna_degree": round(lagna_degree % 30, 2),
    "houses": houses,
    "planets": planet_data,

    # Panchang
    "nakshatra": nakshatra,
    "tithi_name": tithi_name,
    "tithi_number": tithi_number,
    "yoga_number": yoga_number,
    "karana_number": karana_number,
    "ayanamsa": round(ayanamsa, 4)
    }

    '''

#============================================================================
'''
import swisseph as swe
from datetime import datetime, timedelta


# ==============================
# SETTINGS
# ==============================

EPHE_PATH = '.'
IST_HOURS = 5
IST_MINUTES = 30

NAK_DIV = 360.0 / 27.0  # exact: 13.333333333333334


# ==============================
# NAME ARRAYS
# ==============================

RASHI_NAMES = [
    "Mesha", "Vrishabha", "Mithuna", "Karka",
    "Simha", "Kanya", "Tula", "Vrischika",
    "Dhanu", "Makara", "Kumbha", "Meena"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

# Full 30 Tithi names (Shukla 1-15 + Krishna 1-15)
TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",     # Shukla
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"     # Krishna
]

YOGA_NAMES = [
    "Vishkumbha", "Preeti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shoola", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti"
]

KARANA_NAMES = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti"]

# Planets to calculate (MEAN_NODE for standard Vedic Rahu)
PLANET_LIST = [
    ("Sun",     swe.SUN),
    ("Moon",    swe.MOON),
    ("Mercury", swe.MERCURY),
    ("Venus",   swe.VENUS),
    ("Mars",    swe.MARS),
    ("Jupiter", swe.JUPITER),
    ("Saturn",  swe.SATURN),
    ("Rahu",    swe.MEAN_NODE),   # TRUE_NODE causes ~1° error vs reference apps
]

# Consistent flags for all planet calculations
PLANET_FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED


# ==============================
# HELPERS
# ==============================

def to_dms(deg):
    """Convert decimal degrees to degrees°minutes' string."""
    deg = abs(deg)
    d = int(deg)
    m = int((deg - d) * 60)
    return f"{d}°{m:02d}'"


def get_nakshatra_pada(lon):
    """Return (nakshatra_name, pada 1-4) for a given sidereal longitude."""
    idx = int(lon / NAK_DIV) % 27
    pada = int((lon % NAK_DIV) / (NAK_DIV / 4)) + 1
    return NAKSHATRAS[idx], pada


def ist_to_jd(year, month, day, hour, minute, second=0):
    """Convert IST birth time to Julian Day (UTC)."""
    dt_ist = datetime(year, month, day, hour, minute, second)
    dt_utc = dt_ist - timedelta(hours=IST_HOURS, minutes=IST_MINUTES)
    return swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    )


# ==============================
# MAIN ENGINE
# ==============================

def calculate_kundali(year, month, day, hour, minute, lat, lon):
    """
    Calculate a complete Vedic Kundali.

    Args:
        year, month, day : birth date
        hour, minute     : birth time in IST (24h)
        lat, lon         : birth place coordinates

    Returns:
        dict with lagna, houses, planets, panchang, ayanamsa
    """

    # Always set explicitly — never rely on global state from other modules
    swe.set_ephe_path(EPHE_PATH)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # ---- Julian Day ----
    jd = ist_to_jd(year, month, day, hour, minute)

    # ---- Lagna (Ascendant) ----
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    lagna_lon = ascmc[0]
    lagna_sign_index = int(lagna_lon / 30)
    lagna_sign = RASHI_NAMES[lagna_sign_index]
    lagna_nak, lagna_pada = get_nakshatra_pada(lagna_lon)

    # ---- House buckets ----
    houses = {i: [] for i in range(1, 13)}
    houses[1].append("Lagna")

    # ---- Planet Positions ----
    planet_data = []

    for name, planet_id in PLANET_LIST:
        data = swe.calc_ut(jd, planet_id, PLANET_FLAGS)
        raw_lon = data[0][0]
        speed = data[0][3]

        sign_index = int(raw_lon / 30)
        sign_name = RASHI_NAMES[sign_index]
        house_number = ((sign_index - lagna_sign_index) % 12) + 1
        nak_name, pada = get_nakshatra_pada(raw_lon)

        houses[house_number].append(name)

        planet_data.append({
            "name":             name,
            "sign":             sign_name,
            "degree":           to_dms(raw_lon % 30),        # DMS format: 2°57'
            "degree_decimal":   round(raw_lon % 30, 4),      # for internal calculations
            "house":            house_number,
            "nakshatra":        nak_name,
            "pada":             pada,
            "retrograde":       speed < 0,
            "_raw_lon":         raw_lon                       # internal — used for Ketu
        })

    # ---- Ketu (always 180° from Rahu) ----
    # Use _raw_lon to avoid double-rounding error
    rahu_entry = next(p for p in planet_data if p["name"] == "Rahu")
    ketu_lon = (rahu_entry["_raw_lon"] + 180.0) % 360.0

    ketu_sign_index = int(ketu_lon / 30)
    ketu_sign = RASHI_NAMES[ketu_sign_index]
    ketu_house = ((ketu_sign_index - lagna_sign_index) % 12) + 1
    ketu_nak, ketu_pada = get_nakshatra_pada(ketu_lon)

    houses[ketu_house].append("Ketu")

    planet_data.append({
        "name":           "Ketu",
        "sign":           ketu_sign,
        "degree":         to_dms(ketu_lon % 30),
        "degree_decimal": round(ketu_lon % 30, 4),
        "house":          ketu_house,
        "nakshatra":      ketu_nak,
        "pada":           ketu_pada,
        "retrograde":     True,          # Ketu is always retrograde
        "_raw_lon":       ketu_lon
    })

    # ---- Strip internal _raw_lon before returning ----
    planets_out = [{k: v for k, v in p.items() if k != "_raw_lon"}
                   for p in planet_data]

    # ---- Panchang from chart ----
    sun_entry  = next(p for p in planet_data if p["name"] == "Sun")
    moon_entry = next(p for p in planet_data if p["name"] == "Moon")

    sun_lon  = sun_entry["_raw_lon"]
    moon_lon = moon_entry["_raw_lon"]
    diff = (moon_lon - sun_lon) % 360.0

    # Tithi (1–30)
    tithi_number = int(diff / 12.0) + 1
    tithi_name   = TITHI_NAMES[tithi_number - 1]
    paksha       = "Shukla" if tithi_number <= 15 else "Krishna"
    tithi_progress = round((diff % 12.0) / 12.0 * 100, 2)

    # Nakshatra of Moon
    moon_nak, moon_pada = get_nakshatra_pada(moon_lon)

    # Yoga
    yoga_index = int(((sun_lon + moon_lon) % 360.0) / NAK_DIV) % 27
    yoga_name  = YOGA_NAMES[yoga_index]

    # Karana
    karana_index = int(diff / 6.0) % 7
    karana_name  = KARANA_NAMES[karana_index]

    # Ayanamsa
    ayanamsa = swe.get_ayanamsa(jd)

    # ==============================
    # RETURN
    # ==============================

    return {
        # Lagna
        "lagna":              lagna_sign,
        "lagna_degree":       to_dms(lagna_lon % 30),
        "lagna_degree_decimal": round(lagna_lon % 30, 4),
        "lagna_nakshatra":    lagna_nak,
        "lagna_pada":         lagna_pada,

        # Houses
        "houses":             houses,

        # Planets (Rahu + Ketu included, Nakshatra + Pada for all)
        "planets":            planets_out,

        # Panchang
        "tithi_number":       tithi_number,
        "tithi_name":         tithi_name,
        "paksha":             paksha,
        "tithi_progress":     tithi_progress,
        "nakshatra":          moon_nak,
        "nakshatra_pada":     moon_pada,
        "yoga_name":          yoga_name,
        "karana_name":        karana_name,

        # Meta
        "ayanamsa":           round(ayanamsa, 4),
        "jd":                 round(jd, 6),
    }

    '''


#========================================

"""
kundali_engine.py — AstroLogic Core Engine
Single source of truth for all Vedic kundali calculations.
Uses Sanskrit sign names throughout for consistency.
"""
import swisseph as swe
from datetime import datetime, timedelta

# ==============================
# SETTINGS
# ==============================
EPHE_PATH   = '.'
IST_HOURS   = 5
IST_MINUTES = 30
NAK_DIV     = 360.0 / 27.0   # exact: 13.333333...

# ==============================
# NAME ARRAYS  (Sanskrit — used everywhere)
# ==============================
RASHI_NAMES = [
    "Mesha","Vrishabha","Mithuna","Karka",
    "Simha","Kanya","Tula","Vrischika",
    "Dhanu","Makara","Kumbha","Meena"
]

NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
    "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha",
    "Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha",
    "Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
    "Uttara Bhadrapada","Revati"
]

TITHI_NAMES = [
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami",
    "Shashthi","Saptami","Ashtami","Navami","Dashami",
    "Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Purnima",
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami",
    "Shashthi","Saptami","Ashtami","Navami","Dashami",
    "Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Amavasya"
]

YOGA_NAMES = [
    "Vishkumbha","Preeti","Ayushman","Saubhagya","Shobhana",
    "Atiganda","Sukarma","Dhriti","Shoola","Ganda",
    "Vriddhi","Dhruva","Vyaghata","Harshana","Vajra",
    "Siddhi","Vyatipata","Variyana","Parigha","Shiva",
    "Siddha","Sadhya","Shubha","Shukla","Brahma",
    "Indra","Vaidhriti"
]

KARANA_NAMES = ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"]

# Vimshottari Dasha sequence & years
DASHA_SEQUENCE = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
DASHA_YEARS    = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}

# House lords (Sanskrit signs)
HOUSE_LORDS = {
    "Mesha":"Mars","Vrishabha":"Venus","Mithuna":"Mercury","Karka":"Moon",
    "Simha":"Sun","Kanya":"Mercury","Tula":"Venus","Vrischika":"Mars",
    "Dhanu":"Jupiter","Makara":"Saturn","Kumbha":"Saturn","Meena":"Jupiter"
}

# Exaltation / Debilitation / Own signs (Sanskrit)
EXALTATION   = {"Sun":"Mesha","Moon":"Vrishabha","Mars":"Makara","Mercury":"Kanya",
                 "Jupiter":"Karka","Venus":"Meena","Saturn":"Tula","Rahu":"Mithuna","Ketu":"Dhanu"}
DEBILITATION = {"Sun":"Tula","Moon":"Vrischika","Mars":"Karka","Mercury":"Meena",
                 "Jupiter":"Makara","Venus":"Kanya","Saturn":"Mesha","Rahu":"Dhanu","Ketu":"Mithuna"}
OWN_SIGNS    = {"Sun":["Simha"],"Moon":["Karka"],"Mars":["Mesha","Vrischika"],
                "Mercury":["Mithuna","Kanya"],"Jupiter":["Dhanu","Meena"],
                "Venus":["Vrishabha","Tula"],"Saturn":["Makara","Kumbha"]}

# Planet list for kundali
PLANET_LIST = [
    ("Sun",     swe.SUN),
    ("Moon",    swe.MOON),
    ("Mercury", swe.MERCURY),
    ("Venus",   swe.VENUS),
    ("Mars",    swe.MARS),
    ("Jupiter", swe.JUPITER),
    ("Saturn",  swe.SATURN),
    ("Rahu",    swe.MEAN_NODE),
]

PLANET_FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

# Gandmool nakshatras for dosha
GANDMOOL_NAKS = {"Ashwini","Ashlesha","Magha","Jyeshtha","Mula","Revati"}

# ==============================
# HELPERS
# ==============================

def to_dms(deg):
    deg = abs(deg)
    d = int(deg)
    m = int((deg - d) * 60)
    return f"{d}°{m:02d}'"

def get_nakshatra_pada(lon):
    idx  = int(lon / NAK_DIV) % 27
    pada = int((lon % NAK_DIV) / (NAK_DIV / 4)) + 1
    return NAKSHATRAS[idx], pada

def ist_to_jd(year, month, day, hour, minute, second=0):
    dt_ist = datetime(year, month, day, hour, minute, second)
    dt_utc = dt_ist - timedelta(hours=IST_HOURS, minutes=IST_MINUTES)
    return swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    )

def planet_strength_label(name, sign):
    if EXALTATION.get(name) == sign:   return "Exalted"
    if DEBILITATION.get(name) == sign: return "Debilitated"
    if sign in OWN_SIGNS.get(name,[]):  return "Own Sign"
    return "Neutral"

def get_planet_map(planets):
    return {p["name"]: p for p in planets}

def house_of(pmap, name):
    return pmap.get(name, {}).get("house", 0)

def sign_of(pmap, name):
    return pmap.get(name, {}).get("sign", "")

def raw_lon_of(pmap, name):
    return pmap.get(name, {}).get("_raw_lon", 0)

def planets_in_house(pmap, h):
    return [n for n, p in pmap.items() if p.get("house") == h]

# ==============================
# NAVAMSA (D9)
# ==============================
MOVABLE_SIGNS = {"Mesha","Karka","Tula","Makara"}
FIXED_SIGNS   = {"Vrishabha","Simha","Vrischika","Kumbha"}

def calculate_navamsa_sign(raw_lon):
    sign_index = int(raw_lon / 30)
    sign_name  = RASHI_NAMES[sign_index]
    deg_in_sign = raw_lon % 30
    nav_num = int(deg_in_sign / (30/9))  # 0-8

    if sign_name in MOVABLE_SIGNS:
        start = sign_index
    elif sign_name in FIXED_SIGNS:
        start = (sign_index + 8) % 12
    else:  # dual
        start = (sign_index + 4) % 12

    return RASHI_NAMES[(start + nav_num) % 12]

# ==============================
# DASHA
# ==============================

def calculate_dasha(moon_lon, moon_nak):
    nak_idx  = NAKSHATRAS.index(moon_nak)
    lord     = DASHA_SEQUENCE[nak_idx % 9]
    nak_size = NAK_DIV
    remainder = moon_lon % nak_size
    balance_fraction = (nak_size - remainder) / nak_size
    balance_years = balance_fraction * DASHA_YEARS[lord]
    return lord, round(balance_years, 2)

def get_antardasha(maha_lord):
    start_idx = DASHA_SEQUENCE.index(maha_lord)
    maha_yrs  = DASHA_YEARS[maha_lord]
    return [
        {"lord": DASHA_SEQUENCE[(start_idx+i)%9],
         "years": round((maha_yrs * DASHA_YEARS[DASHA_SEQUENCE[(start_idx+i)%9]]) / 120, 2)}
        for i in range(9)
    ]

# ==============================
# YOGA ENGINE
# ==============================

def calculate_yogas(planets, lagna_sign, houses):
    pmap = get_planet_map(planets)
    yogas = []

    def add(name, desc, present, strength="Medium"):
        yogas.append({"name":name,"description":desc,"present":bool(present),"strength":strength if present else "Absent"})

    KENDRA   = {1,4,7,10}
    TRIKONA  = {1,5,9}
    DUSTHANA = {6,8,12}

    lagna_idx = RASHI_NAMES.index(lagna_sign)

    jup_h  = house_of(pmap,"Jupiter");  jup_s  = sign_of(pmap,"Jupiter")
    ven_h  = house_of(pmap,"Venus");    ven_s  = sign_of(pmap,"Venus")
    mer_h  = house_of(pmap,"Mercury");  mer_s  = sign_of(pmap,"Mercury")
    moon_h = house_of(pmap,"Moon");     moon_s = sign_of(pmap,"Moon")
    sun_h  = house_of(pmap,"Sun");      sun_s  = sign_of(pmap,"Sun")
    sat_h  = house_of(pmap,"Saturn");   sat_s  = sign_of(pmap,"Saturn")
    mar_h  = house_of(pmap,"Mars");     mar_s  = sign_of(pmap,"Mars")
    rahu_h = house_of(pmap,"Rahu")
    ketu_h = house_of(pmap,"Ketu")

    # Gajakesari
    gaja = moon_h and jup_h and abs(jup_h - moon_h) in {0,3,6,9}
    add("Gajakesari Yoga","Jupiter in kendra from Moon — wisdom, fame, prosperity",gaja,
        "Strong" if gaja and jup_s in OWN_SIGNS.get("Jupiter",[]) else "Medium")

    # Pancha Mahapurusha
    for pname, ph, ps, yname, ydesc in [
        ("Mars",    mar_h, mar_s, "Ruchaka Yoga",  "Mars in own/exalt in kendra — courage, leadership"),
        ("Mercury", mer_h, mer_s, "Bhadra Yoga",   "Mercury in own/exalt in kendra — intellect, business"),
        ("Jupiter", jup_h, jup_s, "Hamsa Yoga",    "Jupiter in own/exalt in kendra — wisdom, spirituality"),
        ("Venus",   ven_h, ven_s, "Malavya Yoga",  "Venus in own/exalt in kendra — beauty, luxury, love"),
        ("Saturn",  sat_h, sat_s, "Sasa Yoga",     "Saturn in own/exalt in kendra — discipline, authority"),
    ]:
        present = ph in KENDRA and (ps in OWN_SIGNS.get(pname,[]) or EXALTATION.get(pname)==ps)
        add(yname, ydesc, present, "Strong" if present else "Absent")

    # Budhaditya
    add("Budhaditya Yoga","Sun and Mercury conjunct — sharp intellect, government favor",sun_h==mer_h and sun_h!=0)

    # Chandra-Mangala
    add("Chandra-Mangala Yoga","Moon-Mars conjunct or 7th — wealth via unconventional means",
        (moon_h==mar_h) or (moon_h and mar_h and abs(moon_h-mar_h)==6))

    # Dharma-Karmadhipati
    lord_9  = HOUSE_LORDS.get(RASHI_NAMES[(lagna_idx+8)%12])
    lord_10 = HOUSE_LORDS.get(RASHI_NAMES[(lagna_idx+9)%12])
    h9  = house_of(pmap, lord_9)  if lord_9  else 0
    h10 = house_of(pmap, lord_10) if lord_10 else 0
    dkd = lord_9 and lord_10 and lord_9!=lord_10 and ((h9==h10) or (h9==10 and h10==9) or (h9==9 and h10==10))
    add("Dharma-Karmadhipati Yoga","9th and 10th lords conjunct/exchange — exceptional career, dharmic life",dkd,"Strong" if dkd else "Absent")

    # Viparita Raja
    l6  = HOUSE_LORDS.get(RASHI_NAMES[(lagna_idx+5)%12])
    l8  = HOUSE_LORDS.get(RASHI_NAMES[(lagna_idx+7)%12])
    l12 = HOUSE_LORDS.get(RASHI_NAMES[(lagna_idx+11)%12])
    h6  = house_of(pmap,l6)  if l6  else 0
    h8  = house_of(pmap,l8)  if l8  else 0
    h12 = house_of(pmap,l12) if l12 else 0
    vip = (h6 in DUSTHANA and h8 in DUSTHANA) or (h6 in DUSTHANA and h12 in DUSTHANA)
    add("Viparita Raja Yoga","Dusthana lords in dusthana — rise after adversity, resilience",vip)

    # Neecha Bhanga
    nbry = False
    for planet, deb_sign in DEBILITATION.items():
        p = pmap.get(planet)
        if p and p["sign"]==deb_sign:
            disp = HOUSE_LORDS.get(deb_sign)
            if disp and house_of(pmap,disp) in KENDRA:
                nbry = True; break
    add("Neecha Bhanga Raja Yoga","Debilitation cancelled by dispositor in kendra — weakness becomes power",nbry,"Strong" if nbry else "Absent")

    # Raj Yoga (kendra+trikona lord same planet)
    kendra_lords  = {HOUSE_LORDS.get(RASHI_NAMES[(lagna_idx+h-1)%12]) for h in KENDRA}
    trikona_lords = {HOUSE_LORDS.get(RASHI_NAMES[(lagna_idx+h-1)%12]) for h in TRIKONA}
    raj = bool(kendra_lords & trikona_lords - {None})
    add("Raj Yoga","Same planet lords kendra and trikona — power, success, authority",raj)

    # Dhana Yoga
    lord_2  = HOUSE_LORDS.get(RASHI_NAMES[(lagna_idx+1)%12])
    lord_11 = HOUSE_LORDS.get(RASHI_NAMES[(lagna_idx+10)%12])
    dhana = lord_2 and lord_11 and house_of(pmap,lord_2)==house_of(pmap,lord_11) and lord_2!=lord_11
    add("Dhana Yoga","Lords of 2nd and 11th conjunct — strong wealth accumulation",dhana)

    # Kemadruma (negative)
    adj = [p for p in planets_in_house(pmap,((moon_h-2)%12)+1)+planets_in_house(pmap,(moon_h%12)+1) if p not in ("Moon","Rahu","Ketu")]
    add("Kemadruma Yoga ⚠","Moon isolated — emotional instability (challenging yoga)",len(adj)==0 and moon_h!=0,"Challenging")

    # Shubha Kartari
    BENEFICS = {"Jupiter","Venus","Moon","Mercury"}
    shubha = (any(p in BENEFICS for p in planets_in_house(pmap,2)) and
              any(p in BENEFICS for p in planets_in_house(pmap,12)))
    add("Shubha Kartari Yoga","Lagna flanked by benefics — protection and good fortune",shubha)

    return yogas

# ==============================
# DOSHA ENGINE
# ==============================

def calculate_doshas(planets, lagna_sign, houses):
    pmap = get_planet_map(planets)
    doshas = []

    def add(name, present, severity, desc, remedies):
        doshas.append({"name":name,"present":bool(present),"severity":severity if present else "None","description":desc,"remedies":remedies})

    mar_h  = house_of(pmap,"Mars")
    rahu_h = house_of(pmap,"Rahu")
    ketu_h = house_of(pmap,"Ketu")
    sun_h  = house_of(pmap,"Sun")
    moon_h = house_of(pmap,"Moon")
    moon_s = sign_of(pmap,"Moon")
    sat_s  = sign_of(pmap,"Saturn")

    # Mangal Dosha
    manglik = mar_h in {1,2,4,7,8,12}
    add("Mangal Dosha (Manglik)", manglik,
        "High" if mar_h in {1,7,8} else "Medium",
        f"Mars in house {mar_h}. Indicates delay/challenges in marriage, conflict with spouse.",
        ["Marry after age 28","Kumbh Vivah ritual","Recite Hanuman Chalisa daily",
         "Donate red lentils on Tuesdays","Wear coral after astrological consultation"])

    # Sade Sati
    moon_idx = RASHI_NAMES.index(moon_s) if moon_s in RASHI_NAMES else -1
    sat_idx  = RASHI_NAMES.index(sat_s)  if sat_s  in RASHI_NAMES else -1
    sade = moon_idx>=0 and sat_idx>=0 and (sat_idx-moon_idx)%12 in {0,1,11}
    add("Shani Sade Sati", sade, "High",
        "Saturn transiting Moon sign ±1 — 7.5-year period of karmic tests and transformation.",
        ["Chant Shani mantra on Saturdays","Donate black sesame seeds",
         "Serve poor and elderly","Recite Shani Stotra regularly"])

    # Kaal Sarp
    if rahu_h and ketu_h:
        all_h = [p["house"] for n,p in pmap.items() if n not in ("Rahu","Ketu","Lagna") and p.get("house")]
        def between(h):
            if rahu_h < ketu_h: return rahu_h < h < ketu_h
            else: return h > rahu_h or h < ketu_h
        ks = bool(all_h) and all(between(h) for h in all_h)
    else:
        ks = False
    add("Kaal Sarp Dosha", ks, "High",
        "All planets between Rahu-Ketu axis — delays, obstacles, karmic challenges.",
        ["Kaal Sarp Puja at Trimbakeshwar","Recite Panchakshara Stotra",
         "Nag Panchami milk offering","Donate blankets on Saturdays"])

    # Pitru Dosha
    h9_planets = planets_in_house(pmap,9)
    pitru = sun_h==9 and any(p in {"Rahu","Ketu","Saturn"} for p in h9_planets) or "Rahu" in h9_planets or "Ketu" in h9_planets
    add("Pitru Dosha", pitru, "Medium",
        "Affliction in 9th house — ancestral karmic debt needing resolution.",
        ["Pitru Tarpan on Amavasya","Donate food to Brahmins",
         "Recite Gayatri Mantra 108 times daily","Plant Peepal tree"])

    # Grahan Dosha
    grahan = ((sun_h==rahu_h and sun_h) or (sun_h==ketu_h and sun_h) or
              (moon_h==rahu_h and moon_h) or (moon_h==ketu_h and moon_h))
    add("Grahan Dosha", grahan, "High",
        "Sun or Moon eclipsed by Rahu/Ketu — affects health, mental clarity, self-confidence.",
        ["Recite Surya/Chandra mantra for afflicted planet",
         "Donate on eclipse days","Worship Surya at sunrise daily"])

    # Gandmool
    moon_nak = pmap.get("Moon",{}).get("nakshatra","")
    gand = moon_nak in GANDMOOL_NAKS
    add("Gandmool Dosha", gand, "Medium",
        f"Moon in {moon_nak} (Gandmool nakshatra) — needs ritual purification.",
        ["Gandmool Shanti Puja in first year","Recite nakshatra mantra",
         "Donate white items on Mondays"])

    return doshas

# ==============================
# SCORING ENGINE
# ==============================

def calculate_chart_scores(planets, lagna_sign, houses):
    pmap = get_planet_map(planets)
    KENDRA   = {1,4,7,10}
    TRIKONA  = {1,5,9}
    DUSTHANA = {6,8,12}
    lagna_idx = RASHI_NAMES.index(lagna_sign)

    def ps(name):
        p = pmap.get(name)
        if not p: return 5
        label = planet_strength_label(name, p["sign"])
        b = {"Exalted":10,"Own Sign":8,"Neutral":5,"Debilitated":2}[label]
        h = p["house"]
        if h in KENDRA:   b += 1
        if h in TRIKONA:  b += 1
        if h in DUSTHANA: b -= 2
        if p.get("retrograde"): b -= 1
        return max(0, min(10, b))

    def lord_of(house_num):
        return HOUSE_LORDS.get(RASHI_NAMES[(lagna_idx + house_num - 1) % 12], "")

    overall  = sum(ps(p) for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"])
    career   = ps("Sun")*1.5 + ps("Saturn")*1.5 + ps("Mars") + ps(lord_of(10))*2
    finance  = ps("Jupiter")*2 + ps("Venus")*1.5 + ps(lord_of(2))*1.5 + ps(lord_of(11))
    marriage = ps("Venus")*2 + ps("Jupiter")*1.5 + ps(lord_of(7))*2 + ps("Moon")*0.5
    health   = ps("Sun")*1.5 + ps("Mars")*1.5 + ps(lord_of(1))*2 + ps(lord_of(6))
    mental   = ps("Moon")*2.5 + ps("Mercury")*2 + ps(lord_of(4))*1.5
    ketu_h   = house_of(pmap,"Ketu")
    spirit   = ps("Jupiter")*2 + ps(lord_of(9))*2 + (7 if ketu_h in {1,5,9,12} else 5)

    def norm(val, denom): return round(min((val/denom)*100, 100))

    return {
        "overall_strength":  norm(overall, 70),
        "career_score":      norm(career, 60),
        "finance_score":     norm(finance, 60),
        "marriage_score":    norm(marriage, 60),
        "health_score":      norm(health, 60),
        "mental_score":      norm(mental, 60),
        "spirituality_score":norm(spirit, 40),
    }

# ==============================
# MAIN KUNDALI ENGINE
# ==============================

def calculate_kundali(year, month, day, hour, minute, lat, lon):
    swe.set_ephe_path(EPHE_PATH)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    jd = ist_to_jd(year, month, day, hour, minute)

    # Lagna
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    lagna_lon = ascmc[0]
    lagna_idx = int(lagna_lon / 30)
    lagna_sign = RASHI_NAMES[lagna_idx]
    lagna_nak, lagna_pada = get_nakshatra_pada(lagna_lon)

    houses     = {i: [] for i in range(1,13)}
    houses[1].append("Lagna")
    planet_data = []

    for name, planet_id in PLANET_LIST:
        data    = swe.calc_ut(jd, planet_id, PLANET_FLAGS)
        raw_lon = data[0][0]
        speed   = data[0][3]

        sign_idx     = int(raw_lon / 30)
        sign_name    = RASHI_NAMES[sign_idx]
        house_number = ((sign_idx - lagna_idx) % 12) + 1
        nak_name, pada = get_nakshatra_pada(raw_lon)
        nav_sign = calculate_navamsa_sign(raw_lon)
        strength = planet_strength_label(name, sign_name)

        houses[house_number].append(name)
        planet_data.append({
            "name":           name,
            "sign":           sign_name,
            "degree":         to_dms(raw_lon % 30),
            "degree_decimal": round(raw_lon % 30, 4),
            #"house":          house_number,
            "house":          int(raw_lon / 30) + 1,
            "nakshatra":      nak_name,
            "pada":           pada,
            "navamsa":        nav_sign,
            "strength":       strength,
            "retrograde":     speed < 0,
            "_raw_lon":       raw_lon,
        })

    # Ketu
    rahu_raw = next(p for p in planet_data if p["name"]=="Rahu")["_raw_lon"]
    ketu_lon = (rahu_raw + 180.0) % 360.0
    ketu_idx = int(ketu_lon / 30)
    ketu_sign = RASHI_NAMES[ketu_idx]
    ketu_house = ((ketu_idx - lagna_idx) % 12) + 1
    ketu_nak, ketu_pada = get_nakshatra_pada(ketu_lon)
    houses[ketu_house].append("Ketu")
    planet_data.append({
        "name":"Ketu","sign":ketu_sign,
        "degree":to_dms(ketu_lon%30),"degree_decimal":round(ketu_lon%30,4),
        "house":ketu_idx+1,"nakshatra":ketu_nak,"pada":ketu_pada,
        "navamsa":calculate_navamsa_sign(ketu_lon),
        "strength":planet_strength_label("Ketu",ketu_sign),
        "retrograde":True,"_raw_lon":ketu_lon,
    })

    # Panchang
    sun_lon  = next(p for p in planet_data if p["name"]=="Sun")["_raw_lon"]
    moon_lon = next(p for p in planet_data if p["name"]=="Moon")["_raw_lon"]
    diff = (moon_lon - sun_lon) % 360.0

    tithi_number = int(diff / 12.0) + 1
    tithi_name   = TITHI_NAMES[tithi_number - 1]
    paksha       = "Shukla" if tithi_number <= 15 else "Krishna"
    moon_nak, moon_pada = get_nakshatra_pada(moon_lon)
    yoga_name   = YOGA_NAMES[int(((sun_lon+moon_lon)%360)/NAK_DIV)%27]
    karana_name = KARANA_NAMES[int(diff/6.0)%7]
    ayanamsa    = swe.get_ayanamsa(jd)

    # Dasha
    maha_lord, balance_years = calculate_dasha(moon_lon, moon_nak)
    antardasha = get_antardasha(maha_lord)

    # D9 houses
    d9_houses = {i: [] for i in range(1,13)}
    d9_lagna_nav = calculate_navamsa_sign(lagna_lon)
    d9_lagna_idx = RASHI_NAMES.index(d9_lagna_nav)
    d9_houses[1].append("Lagna")
    for p in planet_data:
        if p["name"] == "Lagna": continue
        nav = p.get("navamsa","")
        if nav in RASHI_NAMES:
            nav_idx = RASHI_NAMES.index(nav)
            d9_h = ((nav_idx - d9_lagna_idx) % 12) + 1
            d9_houses[d9_h].append(p["name"])

    # Scores, Yogas, Doshas
    planets_out = [{k:v for k,v in p.items() if k!="_raw_lon"} for p in planet_data]
    scores  = calculate_chart_scores(planet_data, lagna_sign, houses)
    yogas   = calculate_yogas(planet_data, lagna_sign, houses)
    doshas  = calculate_doshas(planet_data, lagna_sign, houses)

    return {
        # Lagna
        "lagna":               lagna_sign,
        "lagna_degree":        to_dms(lagna_lon % 30),
        "lagna_degree_decimal":round(lagna_lon % 30, 4),
        "lagna_nakshatra":     lagna_nak,
        "lagna_pada":          lagna_pada,
        # Houses
        "houses":              houses,
        "d9_houses":           d9_houses,
        "d9_lagna":            d9_lagna_nav,
        # Planets
        "planets":             planets_out,
        # Panchang
        "tithi_number":        tithi_number,
        "tithi_name":          tithi_name,
        "paksha":              paksha,
        "nakshatra":           moon_nak,
        "nakshatra_pada":      moon_pada,
        "yoga_name":           yoga_name,
        "karana_name":         karana_name,
        "ayanamsa":            round(ayanamsa, 4),
        "jd":                  round(jd, 6),
        # Dasha
        "mahadasha":           maha_lord,
        "dasha_balance":       f"{balance_years:.1f} years",
        "antardasha":          antardasha[0]["lord"] if antardasha else "",
        "antardasha_list":     antardasha,
        # Analysis
        "scores":              scores,
        "yogas":               yogas,
        "doshas":              doshas,
    }