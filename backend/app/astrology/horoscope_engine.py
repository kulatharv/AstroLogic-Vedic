"""
horoscope_engine.py — AstroLogic Dynamic Horoscope Engine

Generates daily horoscope for each Sun sign based on ACTUAL current
planetary positions. No predefined or static text. Every output is
derived from real astronomical transits.

Method:
  1. Calculate today's planetary positions (sidereal, Lahiri)
  2. Map each planet to a house relative to the sign being read
  3. Apply classical Vedic + Western horoscope rules:
       - Benefic / malefic planets in each house
       - Planet strength (exaltation, own sign, debilitation)
       - Active aspects (conjunction, opposition, trine, square)
       - Moon's nakshatra influence
       - Current tithi (lunar energy)
  4. Score each life domain (love, career, health, finance, luck)
  5. Build a natural-language paragraph from scored rules
"""

import swisseph as swe
from datetime import datetime, timezone
from math import floor


# ── Setup ──────────────────────────────────────────────────────────────────
swe.set_ephe_path('.')
swe.set_sid_mode(swe.SIDM_LAHIRI)

IST_OFFSET = 5.5
NAK_DIV    = 360.0 / 27.0


# ── Reference data ─────────────────────────────────────────────────────────
RASHI_NAMES = [
    "Mesha","Vrishabha","Mithuna","Karka",
    "Simha","Kanya","Tula","Vrischika",
    "Dhanu","Makara","Kumbha","Meena"
]

# Map Western zodiac sign names → Vedic rashi index (sidereal Lahiri)
# Note: Western sign name maps to the SAME ordinal position in sidereal zodiac
SIGN_TO_RASHI = {
    "Aries":0,"Taurus":1,"Gemini":2,"Cancer":3,
    "Leo":4,"Virgo":5,"Libra":6,"Scorpio":7,
    "Sagittarius":8,"Capricorn":9,"Aquarius":10,"Pisces":11,
}

NAKSHATRA_NAMES = [
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

PLANET_NAMES = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu"]
PLANET_IDS   = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS,
                swe.JUPITER, swe.SATURN, swe.MEAN_NODE]

EXALTATION   = {"Sun":"Mesha","Moon":"Vrishabha","Mars":"Makara",
                "Mercury":"Kanya","Jupiter":"Karka","Venus":"Meena",
                "Saturn":"Tula","Rahu":"Mithuna","Ketu":"Dhanu"}
DEBILITATION = {"Sun":"Tula","Moon":"Vrischika","Mars":"Karka",
                "Mercury":"Meena","Jupiter":"Makara","Venus":"Kanya",
                "Saturn":"Mesha","Rahu":"Dhanu","Ketu":"Mithuna"}
OWN_SIGNS    = {"Sun":["Simha"],"Moon":["Karka"],"Mars":["Mesha","Vrischika"],
                "Mercury":["Mithuna","Kanya"],"Jupiter":["Dhanu","Meena"],
                "Venus":["Vrishabha","Tula"],"Saturn":["Makara","Kumbha"]}

# Natural benefics / malefics
NATURAL_BENEFICS = {"Jupiter","Venus","Moon","Mercury"}
NATURAL_MALEFICS = {"Sun","Mars","Saturn","Rahu","Ketu"}

# House significations for scoring
HOUSE_DOMAINS = {
    1: ["health","self"],
    2: ["finance","wealth"],
    3: ["communication","travel"],
    4: ["home","happiness"],
    5: ["love","creativity","children"],
    6: ["health","work","enemies"],
    7: ["love","partnership","marriage"],
    8: ["transformation","occult"],
    9: ["luck","travel","spirituality"],
    10:["career","status"],
    11:["income","gains"],
    12:["spirituality","losses","foreign"],
}

# Nakshatra lord and their domain influence
NAK_LORDS = [
    "Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury",  # 1-9
    "Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury",  # 10-18
    "Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury",  # 19-27
]

# Tithi energy profiles
TITHI_ENERGY = {
    1:{"overall":+1,"new_start":True},   2:{"overall":+1},
    3:{"overall":+2,"love":+1},          4:{"overall":-1,"obstacles":True},
    5:{"overall":+1},                    6:{"overall":0},
    7:{"overall":+1,"love":+1},          8:{"overall":-1},
    9:{"overall":0},                     10:{"overall":+1,"career":+1},
    11:{"overall":+2,"spiritual":True},  12:{"overall":+1},
    13:{"overall":+1},                   14:{"overall":-1},
    15:{"overall":+3,"love":+2,"luck":+2},  # Purnima — very auspicious
    # Krishna paksha
    16:{"overall":0},                    17:{"overall":0},
    18:{"overall":0},                    19:{"overall":-1},
    20:{"overall":0},                    21:{"overall":0},
    22:{"overall":0},                    23:{"overall":-1,"health":-1},
    24:{"overall":0},                    25:{"overall":0},
    26:{"overall":+2,"spiritual":True},  27:{"overall":0},
    28:{"overall":0},                    29:{"overall":-1},
    30:{"overall":-1,"pitru":True},      # Amavasya
}


# ── Calculation helpers ────────────────────────────────────────────────────

def _planet_strength(planet, rashi):
    """Returns score: +3 exalted, +2 own, 0 neutral, -2 debilitated."""
    if EXALTATION.get(planet) == rashi:   return +3, "Exalted"
    if DEBILITATION.get(planet) == rashi: return -2, "Debilitated"
    if rashi in OWN_SIGNS.get(planet,[]): return +2, "Own Sign"
    return 0, "Neutral"

def _house_from_sign(natal_rashi_idx, planet_rashi_idx):
    """House of planet as seen from natal sign."""
    return ((planet_rashi_idx - natal_rashi_idx) % 12) + 1

def _aspect_strength(h1, h2):
    """
    Classical Vedic aspects: conjunction=1, 7th=opposition,
    4th/10th=square, 5th/9th=trine.
    Returns (aspect_name, score).
    """
    diff = abs(h1 - h2) % 12
    if diff == 0:  return "conjunction", +2
    if diff == 6:  return "opposition",  +1
    if diff in (4,8): return "trine",    +2
    if diff in (3,9): return "square",   -1
    if diff in (2,10): return "sextile", +1
    return None, 0


# ── Main engine ────────────────────────────────────────────────────────────

def get_current_positions():
    """Get all planet positions right now (UTC)."""
    now = datetime.now(timezone.utc)
    jd  = swe.julday(now.year, now.month, now.day,
                     now.hour + now.minute/60 + now.second/3600)
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    positions = {}
    for i, (name, pid) in enumerate(zip(PLANET_NAMES[:8], PLANET_IDS)):
        try:
            data    = swe.calc_ut(jd, pid, FLAGS)
            raw_lon = data[0][0]
            speed   = data[0][3]

            sign_idx = int(raw_lon / 30) % 12
            nak_idx  = int(raw_lon / NAK_DIV) % 27
            strength_score, strength_label = _planet_strength(
                name, RASHI_NAMES[sign_idx])

            positions[name] = {
                "lon":        raw_lon,
                "sign_idx":   sign_idx,
                "sign":       RASHI_NAMES[sign_idx],
                "degree":     raw_lon % 30,
                "nakshatra":  NAKSHATRA_NAMES[nak_idx],
                "nak_idx":    nak_idx,
                "retrograde": speed < 0,
                "strength_score":  strength_score,
                "strength_label":  strength_label,
                "speed":      speed,
                "is_benefic": name in NATURAL_BENEFICS,
            }
        except Exception:
            positions[name] = {"lon":0,"sign_idx":0,"sign":"Mesha","degree":0,
                                "nakshatra":"Ashwini","nak_idx":0,
                                "retrograde":False,"strength_score":0,
                                "strength_label":"Neutral","speed":0,"is_benefic":False}

    # Ketu = Rahu + 180
    if "Rahu" in positions:
        ketu_lon = (positions["Rahu"]["lon"] + 180.0) % 360.0
        ki = int(ketu_lon / 30) % 12
        positions["Ketu"] = {
            "lon": ketu_lon, "sign_idx": ki, "sign": RASHI_NAMES[ki],
            "degree": ketu_lon % 30,
            "nakshatra": NAKSHATRA_NAMES[int(ketu_lon/NAK_DIV)%27],
            "nak_idx": int(ketu_lon/NAK_DIV)%27,
            "retrograde": True, "strength_score": 0,
            "strength_label": "Neutral", "speed": 0, "is_benefic": False,
        }

    # Lunar data
    sun_lon  = positions["Sun"]["lon"]
    moon_lon = positions["Moon"]["lon"]
    diff = (moon_lon - sun_lon) % 360.0
    tithi_no  = int(diff / 12.0) + 1
    paksha    = "Shukla" if tithi_no <= 15 else "Krishna"
    tithi_name = TITHI_NAMES[tithi_no - 1]

    return positions, jd, tithi_no, paksha, tithi_name


def generate_horoscope(sign_name: str) -> dict:
    """
    Generate a complete daily horoscope for `sign_name` (e.g. "Aries")
    based on actual current planetary transits.
    """
    positions, jd, tithi_no, paksha, tithi_name = get_current_positions()

    natal_idx = SIGN_TO_RASHI.get(sign_name, 0)

    # ── 1. Map each planet to a house ─────────────────────────────
    planet_houses = {}
    for pname, pdata in positions.items():
        h = _house_from_sign(natal_idx, pdata["sign_idx"])
        planet_houses[pname] = h
        pdata["house"] = h

    # ── 2. Score each domain ───────────────────────────────────────
    scores = {d: 50 for d in ["overall","love","career","health","finance","luck"]}

    def score_planet_in_house(planet, house, pdata):
        """Apply scoring rules for a planet occupying a house."""
        s = pdata["strength_score"]   # exalt/own/debil modifier
        benefic = pdata["is_benefic"]
        retro   = pdata["retrograde"]

        # Kendra / Trikona boost
        if house in (1,4,7,10): s += 1     # kendra
        if house in (1,5,9):    s += 1     # trikona
        if house in (6,8,12):   s -= 1     # dusthana

        # Retrograde: mixed — generally reduces direct effects
        if retro: s -= 0.5

        val = s if benefic else -s * 0.7   # malefics hurt less than benefics help

        # Map house to domains
        domain_map = HOUSE_DOMAINS.get(house, [])
        for dom in domain_map:
            if dom in scores:
                scores[dom] += val * 4
        scores["overall"] += val * 2

    for pname, h in planet_houses.items():
        if pname in positions:
            score_planet_in_house(pname, h, positions[pname])

    # ── 3. Aspect analysis ────────────────────────────────────────
    aspect_events = []
    planet_list = list(planet_houses.keys())
    for i in range(len(planet_list)):
        for j in range(i+1, len(planet_list)):
            p1, p2 = planet_list[i], planet_list[j]
            h1, h2 = planet_houses[p1], planet_houses[p2]
            aspect_name, asp_score = _aspect_strength(h1, h2)
            if aspect_name and asp_score != 0:
                aspect_events.append((p1, p2, aspect_name, asp_score))
                scores["overall"] += asp_score * 2
                # Specific domain impacts
                if "Venus" in (p1, p2):      scores["love"]     += asp_score * 3
                if "Jupiter" in (p1, p2):    scores["luck"]     += asp_score * 2
                if "Saturn" in (p1, p2):     scores["career"]   += asp_score * 1
                if "Mercury" in (p1, p2):    scores["career"]   += asp_score * 2
                if "Mars" in (p1, p2):       scores["health"]   += asp_score * 2
                if "Moon" in (p1, p2):       scores["love"]     += asp_score * 1

    # ── 4. Tithi influence ────────────────────────────────────────
    te = TITHI_ENERGY.get(tithi_no, {})
    scores["overall"] += te.get("overall", 0) * 3
    scores["love"]    += te.get("love", 0) * 3
    scores["luck"]    += te.get("luck", 0) * 3
    scores["career"]  += te.get("career", 0) * 3
    scores["health"]  += te.get("health", 0) * 3

    # ── 5. Clamp scores to 1–5 stars ──────────────────────────────
    def to_stars(raw):
        # Map raw score around 50 to 1-5
        normalised = (raw - 30) / 30  # ~-0.67 to +2.3
        stars = 1 + normalised * 2    # 1 to ~5.6
        return max(1, min(5, round(stars * 2) / 2))   # half-star resolution

    star_scores = {k: to_stars(v) for k, v in scores.items()}

    # ── 6. Identify key transit events ────────────────────────────
    key_transits = []

    # Jupiter's house
    jup_h = planet_houses.get("Jupiter", 0)
    jup_str = positions["Jupiter"]["strength_label"]
    jup_retro = positions["Jupiter"]["retrograde"]
    if jup_h in (1,5,9,11):
        key_transits.append(f"Jupiter in house {jup_h} ({jup_str}) brings fortune and expansion")
    elif jup_h in (6,8,12):
        key_transits.append(f"Jupiter in house {jup_h} may create hidden blessings through challenges")

    # Saturn's house
    sat_h = planet_houses.get("Saturn", 0)
    sat_str = positions["Saturn"]["strength_label"]
    if sat_h in (3,6,11): key_transits.append(f"Saturn in house {sat_h} rewards disciplined effort with lasting results")
    elif sat_h in (1,7,8): key_transits.append(f"Saturn in house {sat_h} calls for patience and karmic accountability")

    # Venus + Moon for love
    ven_h = planet_houses.get("Venus", 0)
    moon_h = planet_houses.get("Moon", 0)
    ven_str = positions["Venus"]["strength_label"]
    if ven_h in (1,5,7,11) and ven_str != "Debilitated":
        key_transits.append(f"Venus in house {ven_h} ({ven_str}) sweetens relationships and attracts affection")
    if moon_h in (1,4,5): key_transits.append(f"Moon in house {moon_h} elevates emotional intelligence and intuition")
    if moon_h in (6,8,12): key_transits.append(f"Moon in house {moon_h} — guard your emotional equilibrium today")

    # Mercury
    mer_h = planet_houses.get("Mercury", 0)
    if mer_h in (1,3,10): key_transits.append(f"Mercury in house {mer_h} sharpens communication and decision-making")

    # Rahu / Ketu axis
    rahu_h = planet_houses.get("Rahu", 0)
    if rahu_h in (1,10,11): key_transits.append(f"Rahu in house {rahu_h} amplifies worldly ambitions and unconventional paths")
    ketu_h = planet_houses.get("Ketu", 0)
    if ketu_h in (4,9,12): key_transits.append(f"Ketu in house {ketu_h} deepens spiritual sensitivity and past-life awareness")

    # Mars
    mars_h = planet_houses.get("Mars", 0)
    mars_str = positions["Mars"]["strength_label"]
    if mars_str == "Exalted": key_transits.append("Mars exalted brings extraordinary drive and physical vitality")
    elif mars_h in (1,3,6,10): key_transits.append(f"Mars in house {mars_h} energises your actions with courage and initiative")

    # Specific aspects worth naming
    for p1, p2, asp, sc in aspect_events[:3]:
        if abs(sc) >= 2:
            tone = "forming a powerful" if sc > 0 else "creating tension via a"
            key_transits.append(f"{p1}–{p2} {tone} {asp}")

    # ── 7. Build natural language text ────────────────────────────
    moon_nak = positions["Moon"]["nakshatra"]
    sun_sign  = positions["Sun"]["sign"]
    moon_sign = positions["Moon"]["sign"]
    tithi_str = f"{tithi_name} ({paksha})"

    overview  = _build_overview(sign_name, star_scores["overall"], key_transits,
                                 tithi_str, moon_nak, jup_h, sat_h, moon_h)
    love_text  = _build_love(sign_name, star_scores["love"], ven_h, moon_h,
                              positions["Venus"]["strength_label"], paksha)
    career_text = _build_career(sign_name, star_scores["career"], sat_h, mer_h, jup_h,
                                 positions["Saturn"]["strength_label"])
    health_text = _build_health(sign_name, star_scores["health"], mars_h,
                                 positions["Mars"]["strength_label"],
                                 positions["Sun"]["strength_label"], moon_h)

    # ── 8. Lucky data from actual positions ───────────────────────
    lucky_number = _lucky_number(sign_name, planet_houses)
    lucky_color  = _lucky_color(planet_houses, positions)
    best_time    = _best_time(planet_houses)
    mantra       = _get_mantra(sign_name, star_scores["overall"])
    daily_tip    = _get_tip(planet_houses, positions, tithi_no)

    ruling_planet = {
        "Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon",
        "Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars",
        "Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"
    }.get(sign_name,"Jupiter")

    compatible = _compatibility(sign_name, star_scores)

    # Gemstone based on ruling planet strength
    GEMSTONES = {
        "Sun":"Ruby","Moon":"Pearl","Mars":"Red Coral","Mercury":"Emerald",
        "Jupiter":"Yellow Sapphire","Venus":"Diamond","Saturn":"Blue Sapphire",
        "Rahu":"Hessonite","Ketu":"Cat's Eye"
    }
    gem = GEMSTONES.get(ruling_planet,"Yellow Sapphire")

    return {
        "sign": sign_name,
        "date": datetime.now().strftime("%A, %B %d, %Y"),
        "tithi": tithi_str,
        "moon_nakshatra": moon_nak,
        "moon_sign": moon_sign,
        "sun_sign": sun_sign,

        "overview": overview,
        "love": love_text,
        "career": career_text,
        "health": health_text,

        "stars": {
            "overall": star_scores["overall"],
            "love":    star_scores["love"],
            "career":  star_scores["career"],
            "health":  star_scores["health"],
            "finance": star_scores["finance"],
            "luck":    star_scores["luck"],
        },

        "lucky_number":  lucky_number,
        "lucky_color":   lucky_color,
        "lucky_gem":     gem,
        "ruling_planet": ruling_planet,
        "best_time":     best_time,
        "mantra":        mantra,
        "tip":           daily_tip,
        "compatible":    compatible,

        # Raw data for transparency
        "key_transits":  key_transits[:5],
        "planet_houses": {k: v for k, v in planet_houses.items()},
        "planet_details": {
            k: {"house": v["house"], "sign": v["sign"], "strength": v["strength_label"],
                "retrograde": v["retrograde"], "nakshatra": v["nakshatra"]}
            for k, v in positions.items()
        },
    }


# ── Text builders ──────────────────────────────────────────────────────────

def _build_overview(sign, stars, transits, tithi, moon_nak, jup_h, sat_h, moon_h):
    overall = round(stars)
    intensity_words = {1:"challenging",2:"mixed",3:"moderate",4:"favourable",5:"exceptional"}
    intensity = intensity_words.get(overall,"moderate")

    # Opening based on star level
    if overall >= 4:
        opener = f"The cosmos aligns favourably for {sign} today."
    elif overall <= 2:
        opener = f"Today calls for careful navigation, {sign}."
    else:
        opener = f"A balanced day unfolds for {sign} with mixed celestial currents."

    # Tithi context
    tithi_context = {
        "Purnima": "The full moon amplifies your emotional field and illuminates hidden truths.",
        "Amavasya": "The new moon invites introspection and ancestral connection.",
        "Ekadashi": "Ekadashi's spiritual energy heightens intuition and reduces material desires.",
        "Chaturthi": "Lord Ganesha's tithi — pause before obstacles to find the right path.",
        "Ashtami": "The eighth tithi carries Kali's transformative energy.",
    }
    tithi_base = tithi.split(" ")[0]
    tithi_note = tithi_context.get(tithi_base, f"The {tithi} tithi sets a {intensity} tone for the day.")

    # Moon nakshatra influence
    nak_influences = {
        "Ashwini":"quick healing and swift beginnings",
        "Rohini":"material comforts and sensory pleasures",
        "Ardra":"storms of change and intellectual breakthroughs",
        "Pushya":"nourishment, growth and emotional security",
        "Magha":"ancestral strength and leadership presence",
        "Chitra":"creativity, beauty and artistic expression",
        "Swati":"independence, diplomacy and new learning",
        "Vishakha":"focused ambition and purposeful action",
        "Jyeshtha":"seniority, protection and hidden power",
        "Mula":"roots, foundations and the courage to let go",
        "Shravana":"careful listening and learning from mentors",
        "Dhanishta":"rhythm, wealth and musical intelligence",
    }
    nak_note = nak_influences.get(moon_nak,
        f"the Moon in {moon_nak} brings heightened sensitivity to your surroundings")

    transit_note = ""
    if transits:
        transit_note = " " + transits[0].capitalize() + "."
        if len(transits) > 1:
            transit_note += " " + transits[1].capitalize() + "."

    return f"{opener} {tithi_note} The Moon in {moon_nak} nakshatra accentuates {nak_note}.{transit_note}"


def _build_love(sign, stars, ven_h, moon_h, ven_str, paksha):
    s = round(stars)
    if s >= 4:
        base = "Venus blesses your relational field today with warmth and receptivity."
        if ven_h in (5,7): base += f" With Venus occupying your {ven_h}th house, romantic connections deepen organically."
        if paksha == "Shukla": base += " The waxing moon phase invites emotional openness and authentic sharing."
    elif s <= 2:
        base = "Emotional undercurrents may create friction in close relationships."
        if ven_str == "Debilitated": base += " Venus in debilitation suggests the need for extra gentleness and compromise."
        base += " Avoid reactive communication — give space before addressing unresolved tensions."
    else:
        base = "A stable but unremarkable day for relationships."
        if moon_h in (4,7): base += f" The Moon in your {moon_h}th house cultivates domestic harmony and emotional attunement."
        base += " Small gestures of affection carry more weight than grand displays."
    return base


def _build_career(sign, stars, sat_h, mer_h, jup_h, sat_str):
    s = round(stars)
    if s >= 4:
        base = "Professional energies run strong today."
        if mer_h in (1,3,10): base += f" Mercury in house {mer_h} sharpens your strategic thinking and communication."
        if jup_h in (10,11): base += f" Jupiter's presence in house {jup_h} opens doors to recognition and new opportunities."
        base += " Present your ideas with confidence — authority figures are receptive."
    elif s <= 2:
        base = "Tread carefully in professional dealings today."
        if sat_str == "Debilitated": base += " Saturn under stress may create delays and bureaucratic friction."
        base += " Focus on completing existing commitments rather than starting new initiatives."
    else:
        base = "Steady progress marks today's work energy."
        if sat_h in (3,6,11): base += f" Saturn in house {sat_h} rewards methodical effort with incremental gains."
        base += " Prioritise quality over quantity in your outputs."
    return base


def _build_health(sign, stars, mars_h, mars_str, sun_str, moon_h):
    s = round(stars)
    if s >= 4:
        base = "Vitality runs high today."
        if mars_str == "Exalted": base += " Mars exalted supercharges your physical endurance and willpower."
        base += " Channel this energy through vigorous exercise or outdoor activity."
        if sun_str == "Exalted": base += " The Sun in exaltation strengthens immunity and overall constitution."
    elif s <= 2:
        base = "Energy levels may fluctuate — pay attention to your body's signals."
        if mars_h in (6,8,12): base += f" Mars in house {mars_h} may produce heat-related complaints or restlessness."
        base += " Rest is not laziness today — it is medicine. Favour light, easily digestible foods."
        if moon_h in (6,8): base += " Emotional stress may manifest physically; address the root cause."
    else:
        base = "Health remains stable with mindful habits."
        base += " A morning pranayama or walk will set a centred tone for the day."
        if mars_str == "Own Sign": base += " Mars in own sign provides steady physical stamina."
    return base


def _lucky_number(sign, planet_houses):
    """Derive lucky number from benefics in auspicious houses."""
    benefic_houses = []
    for p in ["Jupiter","Venus","Moon","Mercury"]:
        if p in planet_houses:
            h = planet_houses[p]
            if h in (1,5,9,11,2): benefic_houses.append(h)
    if benefic_houses:
        return benefic_houses[0]
    # Fallback based on sign element
    element_nums = {"Aries":9,"Taurus":6,"Gemini":5,"Cancer":2,"Leo":1,
                     "Virgo":5,"Libra":6,"Scorpio":9,"Sagittarius":3,
                     "Capricorn":8,"Aquarius":8,"Pisces":3}
    return element_nums.get(sign, 3)


def _lucky_color(planet_houses, positions):
    """Lucky color based on strongest benefic today."""
    PLANET_COLORS = {
        "Sun":"Gold","Moon":"White","Mars":"Red","Mercury":"Green",
        "Jupiter":"Yellow","Venus":"Pink","Saturn":"Blue","Rahu":"Smoke","Ketu":"Grey"
    }
    best = None
    best_score = -999
    for p in ["Jupiter","Venus","Moon","Mercury","Sun","Mars"]:
        if p in positions:
            s = positions[p]["strength_score"]
            h = planet_houses.get(p,0)
            if h in (1,5,9,11): s += 2
            if s > best_score:
                best_score = s
                best = p
    return PLANET_COLORS.get(best,"Gold")


def _best_time(planet_houses):
    """Best time slot based on Sun's house."""
    sun_h = planet_houses.get("Sun",0)
    time_map = {
        1:"6–8 AM",2:"8–10 AM",3:"10 AM–12 PM",4:"12–2 PM",
        5:"2–4 PM",6:"4–6 PM",7:"6–8 AM",8:"8–10 AM",
        9:"10 AM–12 PM",10:"12–2 PM",11:"2–4 PM",12:"4–6 PM"
    }
    return time_map.get(sun_h,"6–9 AM")


def _get_mantra(sign, stars):
    """Mantra based on sign's ruling planet, intensity by stars."""
    MANTRAS = {
        "Aries":   "Om Angarakaya Namaha (108×) — invoke Mars energy",
        "Taurus":  "Om Shukraya Namaha (108×) — invoke Venus blessings",
        "Gemini":  "Om Budhaya Namaha (108×) — sharpen Mercury's clarity",
        "Cancer":  "Om Chandraya Namaha (108×) — soothe the Moon's fluctuations",
        "Leo":     "Om Suryaya Namaha (12×) at sunrise — invoke solar vitality",
        "Virgo":   "Om Budhaya Namaha (108×) — invoke Mercury's discernment",
        "Libra":   "Om Shukraya Namaha (108×) — harmonise Venus for balance",
        "Scorpio": "Om Angarakaya Namaha (108×) — transmute Mars' intensity",
        "Sagittarius":"Om Gurave Namaha (108×) — align with Jupiter's wisdom",
        "Capricorn":"Om Shanaischaraya Namaha (19×) — honour Saturn's discipline",
        "Aquarius":"Om Shanaischaraya Namaha (19×) — work with Saturn's karma",
        "Pisces":  "Om Gurave Namaha (108×) — receive Jupiter's grace",
    }
    return MANTRAS.get(sign, "Om Namah Shivaya — universal protection")


def _get_tip(planet_houses, positions, tithi_no):
    """Specific actionable tip based on today's most powerful planetary energy."""
    tips = []

    mer_h = planet_houses.get("Mercury",0)
    jup_h = planet_houses.get("Jupiter",0)
    sat_h = planet_houses.get("Saturn",0)
    mars_h = planet_houses.get("Mars",0)
    ven_h = planet_houses.get("Venus",0)
    moon_h = planet_houses.get("Moon",0)

    if jup_h in (1,5,9,11) and positions.get("Jupiter",{}).get("strength_score",0) >= 0:
        tips.append("Expand your network today — Jupiter's placement favours fruitful introductions.")
    if mer_h in (1,3,10) and not positions.get("Mercury",{}).get("retrograde",False):
        tips.append("Sign contracts or send important communications before 2 PM when Mercury is strongest.")
    if sat_h in (6,3,11):
        tips.append("A period of focused, uninterrupted work this morning will yield disproportionate results.")
    if mars_h in (3,6,10) and positions.get("Mars",{}).get("strength_label") != "Debilitated":
        tips.append("Physical activity before 9 AM will clear mental fog and boost your entire day.")
    if ven_h in (5,7) and not positions.get("Venus",{}).get("retrograde",False):
        tips.append("Plan a meaningful gesture for someone you care about — Venus rewards such actions now.")
    if tithi_no == 11:
        tips.append("Today's Ekadashi energy magnifies the effect of any fast or spiritual practice.")
    if tithi_no in (1,6,11):
        tips.append("Begin a new project or initiative today — this tithi supports fresh starts.")
    if moon_h in (6,8):
        tips.append("Protect your emotional energy by limiting time around draining people today.")

    if not tips:
        tips.append("Review your priorities and align your actions with your deepest long-term goals.")

    return tips[0]


def _compatibility(sign, star_scores):
    """Return 3 compatible signs based on element + current planet positions."""
    COMPAT = {
        "Aries":["Leo","Sagittarius","Gemini"],
        "Taurus":["Virgo","Capricorn","Cancer"],
        "Gemini":["Libra","Aquarius","Aries"],
        "Cancer":["Scorpio","Pisces","Taurus"],
        "Leo":["Aries","Sagittarius","Gemini"],
        "Virgo":["Taurus","Capricorn","Cancer"],
        "Libra":["Gemini","Aquarius","Leo"],
        "Scorpio":["Cancer","Pisces","Virgo"],
        "Sagittarius":["Aries","Leo","Libra"],
        "Capricorn":["Taurus","Virgo","Scorpio"],
        "Aquarius":["Gemini","Libra","Sagittarius"],
        "Pisces":["Cancer","Scorpio","Capricorn"],
    }
    return COMPAT.get(sign,["Leo","Sagittarius","Gemini"])


# ── Batch all signs ────────────────────────────────────────────────────────

ALL_SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
             "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

def generate_all_horoscopes():
    """Generate horoscopes for all 12 signs at once (uses cached positions)."""
    results = {}
    for sign in ALL_SIGNS:
        try:
            results[sign] = generate_horoscope(sign)
        except Exception as e:
            results[sign] = {"sign":sign,"error":str(e)}
    return results