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
import swisseph as swe
from datetime import datetime

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
    jd = swe.julday(year, month, day,
                    hour + minute/60 - IST_OFFSET)

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
        data = swe.calc_ut(jd, p, swe.FLG_SIDEREAL | swe.FLG_SPEED)
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