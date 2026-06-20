"""
domain_engine.py — Complete Life Domain Analysis Engine
Covers all 10 life domains using house lords, planet positions,
dasha activation, transits, yogas and divisional charts.
"""
'''

import swisseph as swe
from datetime import datetime, timezone
from math import floor

swe.set_ephe_path('.')
swe.set_sid_mode(swe.SIDM_LAHIRI)

# ═══════════════════════════════════════════════════
# REFERENCE DATA
# ═══════════════════════════════════════════════════

RASHI = ["Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya",
         "Tula","Vrischika","Dhanu","Makara","Kumbha","Meena"]

RASHI_EN = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
            "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
    "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha",
    "Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha",
    "Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
    "Uttara Bhadrapada","Revati",
]

SIGN_LORDS = {
    "Mesha":"Mars","Vrishabha":"Venus","Mithuna":"Mercury","Karka":"Moon",
    "Simha":"Sun","Kanya":"Mercury","Tula":"Venus","Vrischika":"Mars",
    "Dhanu":"Jupiter","Makara":"Saturn","Kumbha":"Saturn","Meena":"Jupiter"
}

DASHA_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
DASHA_YEARS = dict(Ketu=7,Venus=20,Sun=6,Moon=10,Mars=7,Rahu=18,Jupiter=16,Saturn=19,Mercury=17)
NAK_DIV     = 360 / 27

EXALTATION   = dict(Sun="Mesha",Moon="Vrishabha",Mars="Makara",Mercury="Kanya",
                    Jupiter="Karka",Venus="Meena",Saturn="Tula",Rahu="Vrishabha",Ketu="Vrischika")
DEBILITATION = dict(Sun="Tula",Moon="Vrischika",Mars="Karka",Mercury="Meena",
                    Jupiter="Makara",Venus="Kanya",Saturn="Mesha",Rahu="Vrischika",Ketu="Vrishabha")
OWN_SIGNS    = dict(Sun=["Simha"],Moon=["Karka"],Mars=["Mesha","Vrischika"],
                    Mercury=["Mithuna","Kanya"],Jupiter=["Dhanu","Meena"],
                    Venus=["Vrishabha","Tula"],Saturn=["Makara","Kumbha"])

PLANET_IDS = dict(Sun=swe.SUN,Moon=swe.MOON,Mercury=swe.MERCURY,Venus=swe.VENUS,
                  Mars=swe.MARS,Jupiter=swe.JUPITER,Saturn=swe.SATURN,Rahu=swe.TRUE_NODE)

IST = 5.5

def parse_degree(value):
    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        try:
            # Example: "11°58'"
            parts = value.replace("°", " ").replace("'", "").split()
            deg = float(parts[0])
            minute = float(parts[1]) if len(parts) > 1 else 0
            return deg + minute / 60
        except:
            return 0.0

    return 0.0
# ═══════════════════════════════════════════════════
# LOW-LEVEL HELPERS
# ═══════════════════════════════════════════════════

def _planet_strength(name: str, sign: str) -> tuple:
    """Returns (label, score) — score from -2 to +3."""
    if EXALTATION.get(name) == sign:   return "Exalted",      3
    if DEBILITATION.get(name) == sign: return "Debilitated",  -2
    if sign in OWN_SIGNS.get(name,[]):  return "Own Sign",     2
    return "Neutral", 0


def _house_from(planet_sign_idx: int, lagna_sign_idx: int) -> int:
    return ((planet_sign_idx - lagna_sign_idx) % 12) + 1


def _ordinal(n: int) -> str:
    s = {1:"st",2:"nd",3:"rd"}.get(n if n < 20 else n % 10,"th")
    return f"{n}{s}"


def _sign_lord(sign: str) -> str:
    return SIGN_LORDS.get(sign, "Unknown")


def _house_lord(lagna_idx: int, house: int) -> str:
    sign = RASHI[(lagna_idx + house - 1) % 12]
    return _sign_lord(sign)


def _house_sign(lagna_idx: int, house: int) -> str:
    return RASHI[(lagna_idx + house - 1) % 12]


def _nakshatra(lon: float) -> str:
    return NAKSHATRAS[int(lon / NAK_DIV) % 27]


def _aspect_houses(house: int) -> list:
    """Return houses aspected by a planet in `house` (Vedic full aspects)."""
    aspects = {
        1:[7],2:[8],3:[9],4:[10],5:[11],6:[12],
        7:[1],8:[2],9:[3],10:[4],11:[5],12:[6]
    }
    mars_extra  = {1:[4,8],2:[5,9],3:[6,10],4:[7,11],5:[8,12],6:[9,1],
                   7:[10,2],8:[11,3],9:[12,4],10:[1,5],11:[2,6],12:[3,7]}
    return aspects.get(house, [])


def _mars_aspects(house: int) -> list:
    extras = {1:[4,8],2:[5,9],3:[6,10],4:[7,11],5:[8,12],6:[9,1],
              7:[10,2],8:[11,3],9:[12,4],10:[1,5],11:[2,6],12:[3,7]}
    return extras.get(house, [])


def _jupiter_aspects(house: int) -> list:
    extras = {1:[5,9],2:[6,10],3:[7,11],4:[8,12],5:[9,1],6:[10,2],
              7:[11,3],8:[12,4],9:[1,5],10:[2,6],11:[3,7],12:[4,8]}
    return extras.get(house, [])


def _saturn_aspects(house: int) -> list:
    extras = {1:[3,10],2:[4,11],3:[5,12],4:[6,1],5:[7,2],6:[8,3],
              7:[9,4],8:[10,5],9:[11,6],10:[12,7],11:[1,8],12:[2,9]}
    return extras.get(house, [])


# ═══════════════════════════════════════════════════
# CHART EXTRACTION
# ═══════════════════════════════════════════════════

def _build_chart_context(chart: dict) -> dict:
    """
    Normalise the chart dict returned by kundali_engine into a clean
    context object for all domain engines.
    """
    planets   = chart.get("planets", [])
    houses    = chart.get("houses", {})   # {1: ["Sun","Moon",...], ...}
    lagna     = chart.get("lagna", "Mesha")
    lagna_idx = RASHI.index(lagna) if lagna in RASHI else 0
    dob       = chart.get("dob")          # datetime or string

    # Planet → sign, house, strength
    planet_map = {}
    for p in planets:
        name = p.get("name")
        sign = p.get("sign","Mesha")
        house= int(p.get("house", _house_from(RASHI.index(sign) if sign in RASHI else 0, lagna_idx)))
        strength_label, strength_score = _planet_strength(name, sign)
        planet_map[name] = {
            "sign":     sign,
            "house":    house,
            "degree": parse_degree(p.get("degree",0)),
            "retrograde": bool(p.get("retrograde",False)),
            "nakshatra":  p.get("nakshatra",""),
            "strength": strength_label,
            "str_score":strength_score,
        }

    # Ketu = opposite Rahu
    if "Rahu" in planet_map and "Ketu" not in planet_map:
        rahu_h = planet_map["Rahu"]["house"]
        ketu_h = ((rahu_h - 1 + 6) % 12) + 1
        rahu_sign_idx = RASHI.index(planet_map["Rahu"]["sign"]) if planet_map["Rahu"]["sign"] in RASHI else 0
        ketu_sign = RASHI[(rahu_sign_idx + 6) % 12]
        planet_map["Ketu"] = {
            "sign": ketu_sign, "house": ketu_h, "degree": planet_map["Rahu"]["degree"],
            "retrograde": True, "nakshatra": "", "strength": "Neutral", "str_score": 0,
        }

    # House lords
    house_lords = {h: _house_lord(lagna_idx, h) for h in range(1,13)}
    house_signs = {h: _house_sign(lagna_idx, h) for h in range(1,13)}

    # Dasha
    mahadasha = chart.get("mahadasha","")
    antardasha= chart.get("antardasha","")

    # Current transits
    now  = datetime.now(timezone.utc)
    jd_t = swe.julday(now.year,now.month,now.day,now.hour+now.minute/60)
    FLAG = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    transit_map = {}
    for pname, pid in PLANET_IDS.items():
        lon = swe.calc_ut(jd_t, pid, FLAG)[0][0] % 360
        if pname == "Rahu":
            ketu_lon = (lon+180)%360
            transit_map["Ketu"] = {"sign": RASHI[int(ketu_lon/30)],
                                   "house": _house_from(int(ketu_lon/30), lagna_idx)}
        transit_map[pname] = {"sign": RASHI[int(lon/30)],
                              "house": _house_from(int(lon/30), lagna_idx)}

    return {
        "lagna":       lagna,
        "lagna_idx":   lagna_idx,
        "planet_map":  planet_map,
        "house_lords": house_lords,
        "house_signs": house_signs,
        "mahadasha":   mahadasha,
        "antardasha":  antardasha,
        "transit_map": transit_map,
        "yogas":       chart.get("yogas", []),
        "doshas":      chart.get("doshas", []),
        "scores":      chart.get("scores", {}),
    }


# ═══════════════════════════════════════════════════
# SHARED SCORING UTILITY
# ═══════════════════════════════════════════════════

def _score_planets_in_houses(ctx: dict, key_houses: list) -> float:
    """Score based on which planets occupy key_houses and their strengths."""
    planet_map = ctx["planet_map"]
    score = 0.0
    NATURE = dict(Jupiter=3,Venus=2,Moon=1,Mercury=1,Sun=0,Mars=-1,Saturn=-2,Rahu=-1,Ketu=-1)
    for pname, pdata in planet_map.items():
        if pdata["house"] in key_houses:
            n = NATURE.get(pname, 0)
            s = pdata["str_score"]
            h_amp = 1.4 if pdata["house"] in (1,4,7,10) else 1.1 if pdata["house"] in (5,9) else 0.9
            score += (n + s) * h_amp
    return score


def _score_house_lord(ctx: dict, house: int) -> float:
    """Score based on where the house lord is placed and its strength."""
    lord = ctx["house_lords"][house]
    pdata = ctx["planet_map"].get(lord)
    if not pdata: return 0
    h = pdata["house"]
    s = pdata["str_score"]
    # Good placements: 1,2,4,5,7,9,10,11
    h_score = 1 if h in (1,2,4,5,7,9,10,11) else -1
    return s + h_score


def _dasha_activates(ctx: dict, houses: list) -> bool:
    """True if current Mahadasha or Antardasha lord rules or occupies any key house."""
    for dasha_lord in [ctx["mahadasha"], ctx["antardasha"]]:
        if not dasha_lord: continue
        pdata = ctx["planet_map"].get(dasha_lord,{})
        if pdata.get("house") in houses: return True
        for h in houses:
            if ctx["house_lords"].get(h) == dasha_lord: return True
    return False


def _transit_influence(ctx: dict, houses: list, benefic_planets: list) -> float:
    """Score how beneficial current transits are for key houses."""
    score = 0.0
    for pname, tdata in ctx["transit_map"].items():
        if tdata["house"] in houses:
            score += 1.5 if pname in benefic_planets else -1 if pname in ("Saturn","Rahu","Ketu","Mars") else 0
    return score


def _yoga_present(ctx: dict, yoga_names: list) -> list:
    """Return list of active yogas matching any of yoga_names."""
    active = [y.get("name","") if isinstance(y,dict) else str(y) for y in ctx["yogas"] if (isinstance(y,dict) and y.get("present")) or isinstance(y,str)]
    return [y for y in active if any(n.lower() in y.lower() for n in yoga_names)]


def _dosha_present(ctx: dict, dosha_names: list) -> list:
    active = [d.get("name","") if isinstance(d,dict) else str(d) for d in ctx["doshas"] if (isinstance(d,dict) and d.get("present")) or isinstance(d,str)]
    return [d for d in active if any(n.lower() in d.lower() for n in dosha_names)]


def _clamp(v: float, lo=0.0, hi=100.0) -> float:
    return max(lo, min(hi, v))


def _pct(base: float, score: float, dasha_bonus: float = 0) -> int:
    return int(_clamp(50 + score * 6 + dasha_bonus, 10, 98))


# ═══════════════════════════════════════════════════
# TIMING ENGINE
# ═══════════════════════════════════════════════════

def _timing_windows(ctx: dict, key_houses: list, event_name: str) -> dict:
    """
    Generate timing windows using current dasha + transit confluence.
    Returns best period, challenging period, and transit-based windows.
    """
    from datetime import date

    now_year = datetime.now().year
    md = ctx["mahadasha"]
    ad = ctx["antardasha"]

    # Is the event activated right now?
    currently_active = _dasha_activates(ctx, key_houses)
    transit_score    = _transit_influence(ctx, key_houses, ["Jupiter","Venus"])

    # Build next 5 dasha periods for outlook
    md_planet  = ctx["planet_map"].get(md, {})
    md_in_key  = md_planet.get("house") in key_houses

    # Jupiter transit over key houses (approximate 12yr cycle / 1yr per sign)
    jup_house = ctx["transit_map"].get("Jupiter",{}).get("house",1)
    jup_to_key = [(h - jup_house) % 12 for h in key_houses]
    jup_years  = min(jup_to_key) if jup_to_key else 12

    if currently_active and transit_score > 0:
        window = "Now – Next 2 years"
        confidence = "High"
        icon = "🟢"
    elif currently_active:
        window = "Current dasha active — watch Jupiter transit"
        confidence = "Moderate"
        icon = "🟡"
    elif jup_years <= 2:
        window = f"{now_year + jup_years} – {now_year + jup_years + 2}"
        confidence = "Moderate"
        icon = "🟡"
    else:
        window = f"~{now_year + max(2, jup_years)} onward"
        confidence = "Approximate"
        icon = "🔵"

    # Challenging period: Saturn or Rahu transiting key houses
    sat_house = ctx["transit_map"].get("Saturn",{}).get("house",1)
    sat_to_key = min([(h - sat_house) % 12 for h in key_houses], default=12)
    if sat_to_key <= 1:
        challenge = f"Saturn currently in key house — delays and tests until ~{now_year+2}"
    elif sat_to_key <= 3:
        challenge = f"Saturn approaches key house around {now_year + sat_to_key} — plan carefully"
    else:
        challenge = "No immediate Saturn pressure on this domain"

    return {
        "best_window":    f"{icon} {window}",
        "confidence":     confidence,
        "challenge":      challenge,
        "dasha_active":   currently_active,
        "jupiter_years":  jup_years,
    }


# ═══════════════════════════════════════════════════
# REMEDY ENGINE
# ═══════════════════════════════════════════════════

PLANET_REMEDIES = {
    "Sun":     dict(gem="Ruby",mantra="Om Suryaya Namah (108×)",fast="Sunday",donate="Wheat, jaggery, copper"),
    "Moon":    dict(gem="Pearl",mantra="Om Chandraya Namah (108×)",fast="Monday",donate="Rice, white items, milk"),
    "Mars":    dict(gem="Red Coral",mantra="Om Mangalaya Namah (108×)",fast="Tuesday",donate="Red lentils, copper"),
    "Mercury": dict(gem="Emerald",mantra="Om Budhaya Namah (108×)",fast="Wednesday",donate="Green gram, green cloth"),
    "Jupiter": dict(gem="Yellow Sapphire",mantra="Om Gurave Namah (108×)",fast="Thursday",donate="Yellow items, gold, turmeric"),
    "Venus":   dict(gem="Diamond / White Sapphire",mantra="Om Shukraya Namah (108×)",fast="Friday",donate="White items, perfume, silver"),
    "Saturn":  dict(gem="Blue Sapphire",mantra="Om Shanicharaya Namah (108×)",fast="Saturday",donate="Sesame, iron, black items"),
    "Rahu":    dict(gem="Hessonite (Gomed)",mantra="Om Rahave Namah (108×)",fast="Saturday",donate="Coconut, blue items"),
    "Ketu":    dict(gem="Cat's Eye (Lehsunia)",mantra="Om Ketave Namah (108×)",fast="Tuesday",donate="Multi-colored items, sesame"),
}

def _build_remedies(ctx: dict, weak_planets: list, domain: str) -> dict:
    """Build remedy recommendations for a domain based on weak planets."""
    remedies = []
    for p in weak_planets[:2]:  # Top 2 weak planets
        r = PLANET_REMEDIES.get(p, {})
        if r:
            remedies.append({
                "planet":  p,
                "gem":     r["gem"],
                "mantra":  r["mantra"],
                "fast":    r["fast"],
                "donate":  r["donate"],
            })
    # Domain-specific rituals
    DOMAIN_RITUALS = {
        "marriage":    "Offer Swayamvara Parvati puja. Worship Katyayani Devi on Navratri.",
        "career":      "Chant Gayatri Mantra at sunrise. Worship Lord Surya on Sundays.",
        "wealth":      "Perform Lakshmi puja on Fridays with lotus flowers.",
        "health":      "Recite Maha Mrityunjaya Mantra 108× daily. Worship Lord Dhanvantari.",
        "children":    "Santana Gopala mantra. Worship Lord Krishna on Ashtami.",
        "education":   "Saraswati puja on Panchami. Keep books clean and respected.",
        "property":    "Vastu puja before any property purchase. Worship Bhumi Devi.",
        "challenges":  "Hanuman Chalisa on Tuesdays and Saturdays. Navagraha homa.",
        "travel":      "Worship Lord Ganesha before journey. Offer prayers at Kaal Bhairav temple.",
        "spirituality":"Daily Sandhyavandanam. Guru sewa and meditation at Brahma Muhurat.",
    }
    return {
        "planet_remedies": remedies,
        "ritual":          DOMAIN_RITUALS.get(domain, "Perform Navagraha homa for all-round benefit."),
    }


# ═══════════════════════════════════════════════════
# DOMAIN 1 — MARRIAGE & RELATIONSHIPS
# ═══════════════════════════════════════════════════

def analyse_marriage(ctx: dict) -> dict:
    pm = ctx["planet_map"]
    hl = ctx["house_lords"]

    # Core karaka: Venus (7th karaka)
    venus = pm.get("Venus", {})
    jupiter = pm.get("Jupiter", {})
    mars = pm.get("Mars", {})
    moon = pm.get("Moon", {})

    # 7th house
    lord_7 = hl[7]
    lord_7_data = pm.get(lord_7, {})
    lord_7_house = lord_7_data.get("house", 0)
    lord_7_sign  = lord_7_data.get("sign","")
    lord_7_str   = lord_7_data.get("strength","Neutral")

    # 2nd, 5th houses also matter
    h7_occupants = [p for p,d in pm.items() if d["house"]==7]
    h5_occupants = [p for p,d in pm.items() if d["house"]==5]
    h2_occupants = [p for p,d in pm.items() if d["house"]==2]

    # Score
    base  = _score_planets_in_houses(ctx, [7,5,2])
    l7s   = _score_house_lord(ctx, 7)
    venus_score = venus.get("str_score",0) + (2 if venus.get("house") in (7,5,2,1) else 0)
    total_score = base + l7s + venus_score

    dasha_active = _dasha_activates(ctx, [7,5,2])
    transit_sc   = _transit_influence(ctx, [7,5,2], ["Jupiter","Venus"])
    pct = _pct(50, total_score, 10 if dasha_active else 0)

    # Mangal Dosh
    mangal_dosh = mars.get("house") in (1,4,7,8,12)
    mangal_txt = f"Mars in {_ordinal(mars.get('house',0))} house — Mangal Dosh present. Seek dosha cancellation or match with similar chart." if mangal_dosh else "No Mangal Dosh detected."

    # Kalatra Yoga
    kalatra = "Kalatra Yoga" in str(ctx.get("yogas",""))

    # Type of marriage
    if h5_occupants and "Venus" in h5_occupants:
        marriage_type = "Strong indicators of love marriage — Venus in 5th house of romance."
    elif "Jupiter" in h7_occupants:
        marriage_type = "Arranged marriage favoured — Jupiter blesses the 7th house with wisdom and tradition."
    elif "Rahu" in h7_occupants:
        marriage_type = "Unconventional or inter-cultural marriage possible — Rahu influences 7th."
    elif venus.get("house") == 7:
        marriage_type = "Love or love-cum-arranged marriage — Venus directly occupies partnership house."
    else:
        marriage_type = "Arranged marriage most likely — assess 5th house for romance indicators."

    # Partner traits from 7th sign
    sign7 = ctx["house_signs"][7]
    PARTNER_TRAITS = {
        "Mesha":"dynamic, ambitious, independent, sometimes impatient",
        "Vrishabha":"loyal, sensual, patient, materialistic, loves comfort",
        "Mithuna":"witty, communicative, versatile, may be dual-natured",
        "Karka":"caring, emotional, home-loving, intuitive, protective",
        "Simha":"confident, generous, dramatic, needs admiration",
        "Kanya":"analytical, health-conscious, critical, service-oriented",
        "Tula":"charming, diplomatic, aesthetic, partnership-oriented",
        "Vrischika":"intense, secretive, transformative, passionate",
        "Dhanu":"philosophical, adventurous, honest, sometimes blunt",
        "Makara":"disciplined, ambitious, traditional, reliable",
        "Kumbha":"independent, humanitarian, unconventional, intellectual",
        "Meena":"spiritual, compassionate, artistic, sometimes escapist",
    }
    partner_traits = PARTNER_TRAITS.get(sign7, "dignified and balanced")
    if h7_occupants:
        planet_modifiers = {"Venus":"charming and romantic","Jupiter":"wise and spiritual",
                           "Saturn":"mature and serious","Mars":"energetic and assertive",
                           "Mercury":"intelligent and communicative","Moon":"emotional and nurturing",
                           "Sun":"authoritative and proud","Rahu":"exotic or foreign connection",
                           "Ketu":"spiritual or detached"}
        mods = [planet_modifiers[p] for p in h7_occupants if p in planet_modifiers]
        if mods: partner_traits += f" — {', '.join(mods)}"

    # Second marriage
    h8_lord = hl[8]
    h8_data = pm.get(h8_lord,{})
    second_marriage = "Indicators present for second marriage or significant relationship transformation" \
                      if (h8_data.get("house") in (7,2) or "Rahu" in h7_occupants) \
                      else "No strong indicators for second marriage."

    # Chemistry / intimacy (8th house)
    h8_occ = [p for p,d in pm.items() if d["house"]==8]
    intimacy = "Strong physical chemistry" if "Mars" in h8_occ or "Venus" in h8_occ \
               else "Emotional and spiritual connection dominates"

    timing  = _timing_windows(ctx, [7,5,2], "marriage")
    remedies = _build_remedies(ctx,
        [p for p,d in pm.items() if d["house"] in (7,) and d["str_score"]<0] + (["Venus"] if venus.get("str_score",0)<0 else []),
        "marriage")

    return {
        "domain": "Marriage & Relationships",
        "icon":   "♥",
        "score":  pct,
        "marriage_type":   marriage_type,
        "partner_traits":  partner_traits,
        "partner_sign":    f"{sign7} ({RASHI_EN[RASHI.index(sign7)] if sign7 in RASHI else sign7})",
        "mangal_dosh":     mangal_dosh,
        "mangal_dosh_txt": mangal_txt,
        "kalatra_yoga":    kalatra,
        "second_marriage": second_marriage,
        "intimacy":        intimacy,
        "venus_position":  f"Venus in {venus.get('house',0)}H {venus.get('sign','')} — {venus.get('strength','')}",
        "seventh_lord":    f"{lord_7} in {_ordinal(lord_7_house)} house — {lord_7_str}",
        "h7_planets":      h7_occupants,
        "dasha_active":    dasha_active,
        "timing":          timing,
        "remedies":        remedies,
        "analysis":        _marriage_narrative(ctx, pct, marriage_type, partner_traits, timing),
    }


def _marriage_narrative(ctx, pct, mtype, traits, timing):
    md = ctx["mahadasha"]; ad = ctx["antardasha"]
    venus = ctx["planet_map"].get("Venus",{})
    h7 = [p for p,d in ctx["planet_map"].items() if d["house"]==7]
    parts = []
    parts.append(f"Your 7th house of marriage is ruled by {ctx['house_lords'][7]}, and {mtype.lower()}")
    if h7:
        parts.append(f"With {', '.join(h7)} occupying the 7th house, your partnerships carry their energies — {', '.join([str(p) for p in h7])} shapes the nature of your unions.")
    parts.append(f"Venus, the primary karaka for marriage, is placed in the {_ordinal(venus.get('house',1))} house in {venus.get('sign','')} — {venus.get('strength','')}, indicating {'strong' if venus.get('str_score',0)>=0 else 'a challenged'} capacity for love and harmony.")
    parts.append(f"Your partner is likely to be {traits}.")
    parts.append(f"Current {md}/{ad} dasha {'actively triggers' if timing['dasha_active'] else 'does not directly activate'} the marriage houses. Best timing window: {timing['best_window']}.")
    return " ".join(parts)


# ═══════════════════════════════════════════════════
# DOMAIN 2 — CAREER & PROFESSION
# ═══════════════════════════════════════════════════

def analyse_career(ctx: dict) -> dict:
    pm  = ctx["planet_map"]
    hl  = ctx["house_lords"]

    sun    = pm.get("Sun",{})
    saturn = pm.get("Saturn",{})
    mars   = pm.get("Mars",{})
    jupiter= pm.get("Jupiter",{})
    mercury= pm.get("Mercury",{})

    lord_10 = hl[10]; lord_10_data = pm.get(lord_10,{})
    lord_6  = hl[6];  lord_6_data  = pm.get(lord_6,{})
    h10_occ = [p for p,d in pm.items() if d["house"]==10]
    h6_occ  = [p for p,d in pm.items() if d["house"]==6]

    base   = _score_planets_in_houses(ctx, [10,6,11])
    l10s   = _score_house_lord(ctx, 10)
    sun_sc = sun.get("str_score",0) + (2 if sun.get("house") in (10,1,9) else 0)
    total  = base + l10s + sun_sc

    dasha_active = _dasha_activates(ctx, [10,6,11])
    pct = _pct(50, total, 12 if dasha_active else 0)

    # Govt vs private
    sun_strong  = sun.get("str_score",0) >= 1 or sun.get("house") in (10,1)
    saturn_str  = saturn.get("str_score",0)
    if sun_strong and "Sun" in h10_occ:
        sector = "Government / Authority / IAS / Politics — strong Sun in 10th"
    elif saturn.get("house") in (10,6,11):
        sector = "Corporate / Technical / Service sector — Saturn influences career"
    elif mercury.get("house") in (10,6):
        sector = "Business / Communication / Finance / IT — Mercury drives career"
    elif jupiter.get("house") in (10,9):
        sector = "Teaching / Law / Finance / Spirituality — Jupiter in career houses"
    elif mars.get("house") in (10,6):
        sector = "Military / Police / Engineering / Surgery — Mars drives ambition"
    else:
        sector = "Diverse options — multiple planets influence career path"

    # Best fields from 10th sign
    sign10 = ctx["house_signs"][10]
    FIELD_MAP = {
        "Mesha":"engineering, military, sports, surgery",
        "Vrishabha":"finance, banking, agriculture, arts, luxury goods",
        "Mithuna":"journalism, IT, marketing, teaching, trading",
        "Karka":"nursing, real estate, catering, hospitality, social work",
        "Simha":"leadership, politics, entertainment, management, medicine",
        "Kanya":"accounting, medicine, analysis, research, editing",
        "Tula":"law, diplomacy, design, fashion, HR, mediation",
        "Vrischika":"research, intelligence, psychology, occult, mining",
        "Dhanu":"education, law, philosophy, export-import, travel",
        "Makara":"administration, engineering, construction, government",
        "Kumbha":"technology, science, social sector, aviation, astrology",
        "Meena":"spirituality, arts, medicine, marine, photography",
    }
    best_fields = FIELD_MAP.get(sign10,"diverse professional fields")

    # Raja Yoga for career
    raj_yogas = _yoga_present(ctx, ["Raj","Raja","Budhaditya","Dharma Karma"])

    # Promotion timing — 11th house and transits
    h11_lord = hl[11]; h11_data = pm.get(h11_lord,{})
    prom_active = h11_data.get("house") in (1,10,11) or "Jupiter" in [ctx["transit_map"].get("Jupiter",{}).get("house")]

    timing   = _timing_windows(ctx, [10,6,11], "career")
    weak_p   = [p for p,d in pm.items() if d["house"]==10 and d["str_score"]<0]
    if not weak_p and lord_10_data.get("str_score",0)<0: weak_p=[lord_10]
    remedies = _build_remedies(ctx, weak_p + ["Sun"], "career")

    return {
        "domain": "Career & Profession",
        "icon": "★",
        "score": pct,
        "sector": sector,
        "best_fields": best_fields,
        "tenth_lord": f"{lord_10} in {_ordinal(lord_10_data.get('house',0))}H — {lord_10_data.get('strength','')}",
        "h10_planets": h10_occ,
        "raj_yogas": raj_yogas,
        "business_vs_job": "Business favoured" if "Mercury" in h10_occ or mercury.get("house")==10 else "Service/Job favoured" if saturn.get("house")==10 else "Both viable — assess 7th for business",
        "foreign_work": "Strong foreign career indicators" if "Rahu" in h10_occ or ctx["transit_map"].get("Rahu",{}).get("house")==10 else "Domestic career more prominent",
        "dasha_active": dasha_active,
        "timing": timing,
        "remedies": remedies,
        "analysis": _career_narrative(ctx, pct, sector, best_fields, raj_yogas, timing),
    }


def _career_narrative(ctx, pct, sector, fields, yogas, timing):
    md = ctx["mahadasha"]; ad = ctx["antardasha"]
    hl10 = ctx["house_lords"][10]
    h10d = ctx["planet_map"].get(hl10,{})
    parts = []
    parts.append(f"Your 10th house of career is ruled by {hl10}, placed in the {_ordinal(h10d.get('house',1))} house — {h10d.get('strength','Neutral')}.")
    parts.append(f"Career direction points strongly toward {sector}. Best professional fields for your chart: {fields}.")
    if yogas:
        parts.append(f"Powerful career yogas are present: {', '.join(yogas)} — indicating recognition and rise to authority.")
    parts.append(f"Current {md}/{ad} dasha {'actively fires' if timing['dasha_active'] else 'does not directly trigger'} your career houses. Optimal window: {timing['best_window']}.")
    return " ".join(parts)


# ═══════════════════════════════════════════════════
# DOMAIN 3 — WEALTH & FINANCE
# ═══════════════════════════════════════════════════

def analyse_wealth(ctx: dict) -> dict:
    pm = ctx["planet_map"]
    hl = ctx["house_lords"]

    jupiter = pm.get("Jupiter",{})
    venus   = pm.get("Venus",{})
    moon    = pm.get("Moon",{})

    lord_2  = hl[2]; l2d = pm.get(lord_2,{})
    lord_11 = hl[11]; l11d = pm.get(lord_11,{})
    h2_occ  = [p for p,d in pm.items() if d["house"]==2]
    h11_occ = [p for p,d in pm.items() if d["house"]==11]

    base   = _score_planets_in_houses(ctx, [2,11,9,5])
    l2s    = _score_house_lord(ctx, 2)
    l11s   = _score_house_lord(ctx, 11)
    j_sc   = jupiter.get("str_score",0) + (2 if jupiter.get("house") in (2,11,5,9) else 0)
    total  = base + l2s + l11s + j_sc

    dasha_active = _dasha_activates(ctx, [2,11,5,9])
    pct = _pct(50, total, 10 if dasha_active else 0)

    # Dhana Yogas
    dhana_yogas = _yoga_present(ctx, ["Dhana","Lakshmi","Kubera","Wealth"])

    # Income sources from 11th
    sign11 = ctx["house_signs"][11]
    SOURCE_MAP = {
        "Mesha":"business, real estate, initiative-driven income",
        "Vrishabha":"banking, agriculture, luxury trade, accumulation",
        "Mithuna":"communication, media, commission, intellectual work",
        "Karka":"real estate, food industry, family business, water",
        "Simha":"government, leadership, speculation, creative work",
        "Kanya":"service industry, health, detailed analytical work",
        "Tula":"partnerships, trade, legal, design, negotiation",
        "Vrischika":"research, insurance, inheritance, occult",
        "Dhanu":"education, exports, foreign income, law",
        "Makara":"professional services, construction, government",
        "Kumbha":"technology, NGO, innovation, irregular but large gains",
        "Meena":"spiritual services, medicine, arts, sea trade",
    }
    income_sources = SOURCE_MAP.get(sign11,"varied income streams")

    # Sudden gains
    h8_occ  = [p for p,d in pm.items() if d["house"]==8]
    sudden_gain = "Lottery/sudden gains potential" if "Rahu" in h8_occ or "Jupiter" in h8_occ \
                  else "Moderate unexpected income possible" if "Moon" in h8_occ \
                  else "Earned wealth more prominent than windfalls"

    # Debt periods — 6th and 12th affliction
    h6_saturn = pm.get("Saturn",{}).get("house") == 6
    debt_risk  = "Debt risk present — Saturn in 6th. Keep expenses disciplined." if h6_saturn \
                 else "No strong debt indicators in current planetary configuration."

    timing   = _timing_windows(ctx, [2,11,9], "wealth")
    remedies = _build_remedies(ctx, ["Jupiter","Venus"] if j_sc < 0 else (["Jupiter"] if j_sc==0 else []), "wealth")

    return {
        "domain":"Wealth & Finance","icon":"₹","score":pct,
        "dhana_yogas":dhana_yogas,"income_sources":income_sources,
        "sudden_gain":sudden_gain,"debt_risk":debt_risk,
        "second_lord":f"{lord_2} in {_ordinal(l2d.get('house',0))}H — {l2d.get('strength','')}",
        "eleventh_lord":f"{lord_11} in {_ordinal(l11d.get('house',0))}H — {l11d.get('strength','')}",
        "h2_planets":h2_occ,"h11_planets":h11_occ,
        "dasha_active":dasha_active,"timing":timing,"remedies":remedies,
        "analysis":_wealth_narrative(ctx,pct,dhana_yogas,income_sources,timing),
    }


def _wealth_narrative(ctx,pct,yogas,sources,timing):
    md=ctx["mahadasha"]; ad=ctx["antardasha"]
    j=ctx["planet_map"].get("Jupiter",{})
    parts=[]
    parts.append(f"Jupiter, the primary wealth karaka, is placed in the {_ordinal(j.get('house',1))} house in {j.get('sign','')} — {j.get('strength','')}.")
    parts.append(f"Primary income sources: {sources}.")
    if yogas:
        parts.append(f"Dhana Yogas present: {', '.join(yogas)} — strong wealth accumulation potential.")
    parts.append(f"{md}/{ad} dasha {'is actively triggering' if timing['dasha_active'] else 'does not directly trigger'} wealth houses. Best financial window: {timing['best_window']}.")
    return " ".join(parts)


# ═══════════════════════════════════════════════════
# DOMAIN 4 — HEALTH & LONGEVITY
# ═══════════════════════════════════════════════════

def analyse_health(ctx: dict) -> dict:
    pm  = ctx["planet_map"]
    hl  = ctx["house_lords"]

    sun    = pm.get("Sun",{})
    moon   = pm.get("Moon",{})
    saturn = pm.get("Saturn",{})
    mars   = pm.get("Mars",{})

    lord_1 = hl[1]; l1d = pm.get(lord_1,{})
    lord_6 = hl[6]; l6d = pm.get(lord_6,{})
    lord_8 = hl[8]; l8d = pm.get(lord_8,{})

    h1_occ = [p for p,d in pm.items() if d["house"]==1]
    h6_occ = [p for p,d in pm.items() if d["house"]==6]
    h8_occ = [p for p,d in pm.items() if d["house"]==8]

    base  = _score_planets_in_houses(ctx, [1,6,8])
    l1s   = _score_house_lord(ctx, 1)
    sun_sc= sun.get("str_score",0)
    total = base + l1s + sun_sc

    dasha_active = _dasha_activates(ctx, [6,8,12])
    pct = _pct(70, -total, -8 if dasha_active else 0)  # Inverted: higher score = better health

    # Weak organs from 6th/8th house sign
    sign6 = ctx["house_signs"][6]
    ORGAN_MAP = {
        "Mesha":"head, brain, eyes","Vrishabha":"throat, neck, thyroid",
        "Mithuna":"lungs, arms, shoulders","Karka":"chest, stomach, breast",
        "Simha":"heart, spine, upper back","Kanya":"intestines, digestion, skin",
        "Tula":"kidneys, lower back, ovaries","Vrischika":"reproductive organs, excretory",
        "Dhanu":"hips, thighs, liver","Makara":"knees, bones, joints, teeth",
        "Kumbha":"ankles, nervous system, circulation","Meena":"feet, lymphatic, immune",
    }
    lagna_sign = ctx["lagna"]
    weak_organs = ORGAN_MAP.get(sign6,"general constitution")
    lagna_organs = ORGAN_MAP.get(lagna_sign,"overall vitality")

    # Ayurvedic dosha
    DOSHA_MAP = {
        "Mesha":"Pitta","Vrishabha":"Kapha","Mithuna":"Vata","Karka":"Kapha",
        "Simha":"Pitta","Kanya":"Vata","Tula":"Vata","Vrischika":"Pitta",
        "Dhanu":"Pitta","Makara":"Vata","Kumbha":"Vata","Meena":"Kapha",
    }
    ayurvedic_dosha = DOSHA_MAP.get(lagna_sign,"Tridoshic")

    # Arishta doshas
    arishta = _dosha_present(ctx, ["Arishta","Balarishta","Kaal Sarp"])
    mental_h = moon.get("house",1)
    mental_ok = moon.get("str_score",0) >= 0 and mental_h not in (6,8,12)

    surgery_risk = "Mars" in h8_occ or "Mars" in h6_occ or saturn.get("house")==8
    disease_periods = f"Periods to watch: {ctx['mahadasha']} dasha / {ctx['antardasha']} antardasha if Saturn or Mars transits 1st, 6th or 8th"

    timing   = _timing_windows(ctx, [6,8,1], "health")
    remedies = _build_remedies(ctx, ["Sun"] if sun.get("str_score",0)<0 else (["Mars"] if mars.get("str_score",0)<0 else ["Saturn"]), "health")

    return {
        "domain":"Health & Longevity","icon":"✚","score":pct,
        "weak_organs":weak_organs,"lagna_organs":lagna_organs,
        "ayurvedic_dosha":ayurvedic_dosha,"mental_health_ok":mental_ok,
        "surgery_risk":surgery_risk,
        "surgery_txt":"Surgical procedures may come into life — timing matters. Avoid surgery during Mars/Saturn dasha." if surgery_risk else "No strong surgery indicators.",
        "arishta_doshas":arishta,"disease_periods":disease_periods,
        "first_lord":f"{lord_1} in {_ordinal(l1d.get('house',0))}H — {l1d.get('strength','')}",
        "dasha_active":dasha_active,"timing":timing,"remedies":remedies,
        "analysis":_health_narrative(ctx,pct,weak_organs,ayurvedic_dosha,mental_ok),
    }


def _health_narrative(ctx,pct,organs,dosha,mental_ok):
    lagna=ctx["lagna"]; sun=ctx["planet_map"].get("Sun",{}); moon=ctx["planet_map"].get("Moon",{})
    parts=[]
    parts.append(f"Your Lagna (Ascendant) in {lagna} gives a {dosha} constitution — focus on balancing this Ayurvedic dosha through diet, lifestyle and seasonal cleansing.")
    parts.append(f"Vulnerable areas include {organs} — preventive care for these systems is advised.")
    parts.append(f"Sun (vitality karaka) is in the {_ordinal(sun.get('house',1))} house — {sun.get('strength','Neutral')}.")
    parts.append(f"Mental health is {'stable and resilient' if mental_ok else 'sensitive — Moon afflicted; manage stress proactively'}.")
    return " ".join(parts)


# ═══════════════════════════════════════════════════
# DOMAIN 5 — CHILDREN
# ═══════════════════════════════════════════════════

def analyse_children(ctx: dict) -> dict:
    pm = ctx["planet_map"]
    hl = ctx["house_lords"]

    jupiter = pm.get("Jupiter",{}); sun=pm.get("Sun",{}); moon=pm.get("Moon",{})
    lord_5 = hl[5]; l5d = pm.get(lord_5,{})
    h5_occ = [p for p,d in pm.items() if d["house"]==5]
    h9_occ = [p for p,d in pm.items() if d["house"]==9]

    base   = _score_planets_in_houses(ctx, [5,9,1])
    l5s    = _score_house_lord(ctx, 5)
    j_sc   = jupiter.get("str_score",0) + (2 if jupiter.get("house") in (5,9,1) else 0)
    total  = base + l5s + j_sc

    dasha_active = _dasha_activates(ctx, [5,9])
    pct = _pct(50, total, 10 if dasha_active else 0)

    putra_dosh = _dosha_present(ctx, ["Putra","Santana"])
    santana_yoga = _yoga_present(ctx, ["Santana","Putra"])

    # Children count indicator
    j_h = jupiter.get("house",5)
    count = "Multiple children possible" if j_h in (5,11) and jupiter.get("str_score",0)>=0 \
            else "1-2 children indicated" if jupiter.get("str_score",0)>=0 \
            else "Challenges in childbearing — seek remedies"

    # Gender indicator (traditional — not reliable)
    sign5 = ctx["house_signs"][5]
    MALE_SIGNS = ["Mesha","Mithuna","Simha","Dhanu","Kumbha"]
    gender_txt = "Male child indicated" if sign5 in MALE_SIGNS else "Female child indicated"

    child_nature = f"Child likely to be {'creative and intelligent' if 'Jupiter' in h5_occ or 'Mercury' in h5_occ else 'energetic and ambitious' if 'Mars' in h5_occ else 'artistic and sensitive' if 'Venus' in h5_occ or 'Moon' in h5_occ else 'disciplined and serious' if 'Saturn' in h5_occ else 'independent and bright'}"

    timing   = _timing_windows(ctx, [5,9], "children")
    remedies = _build_remedies(ctx, ["Jupiter"] if j_sc<0 else [], "children")

    return {
        "domain":"Children & Next Generation","icon":"❋","score":pct,
        "count_indicator":count,"gender_indicator":gender_txt,
        "child_nature":child_nature,"putra_dosh":putra_dosh,"santana_yoga":santana_yoga,
        "fifth_lord":f"{lord_5} in {_ordinal(l5d.get('house',0))}H — {l5d.get('strength','')}",
        "h5_planets":h5_occ,"jupiter_position":f"Jupiter in {_ordinal(jupiter.get('house',1))}H — {jupiter.get('strength','')}",
        "dasha_active":dasha_active,"timing":timing,"remedies":remedies,
        "analysis":f"Jupiter (putra karaka) in {_ordinal(jupiter.get('house',1))} house ({jupiter.get('strength','')}). 5th lord {lord_5} in {_ordinal(l5d.get('house',1))} house. {count}. {child_nature}. Timing: {timing['best_window']}.",
    }


# ═══════════════════════════════════════════════════
# DOMAIN 6 — EDUCATION & SKILLS
# ═══════════════════════════════════════════════════

def analyse_education(ctx: dict) -> dict:
    pm = ctx["planet_map"]
    hl = ctx["house_lords"]

    mercury = pm.get("Mercury",{}); jupiter = pm.get("Jupiter",{}); sun=pm.get("Sun",{})
    lord_4 = hl[4]; l4d = pm.get(lord_4,{})
    lord_5 = hl[5]; l5d = pm.get(lord_5,{})
    h4_occ = [p for p,d in pm.items() if d["house"]==4]
    h5_occ = [p for p,d in pm.items() if d["house"]==5]

    base  = _score_planets_in_houses(ctx, [4,5,9])
    l4s   = _score_house_lord(ctx, 4)
    l5s   = _score_house_lord(ctx, 5)
    m_sc  = mercury.get("str_score",0)+(1 if mercury.get("house") in (4,5,9) else 0)
    j_sc  = jupiter.get("str_score",0)+(1 if jupiter.get("house") in (4,5,9) else 0)
    total = base + l4s + l5s + m_sc + j_sc

    dasha_active = _dasha_activates(ctx, [4,5,9])
    pct = _pct(50, total, 8 if dasha_active else 0)

    sign4 = ctx["house_signs"][4]
    STUDY_FIELDS = {
        "Mesha":"engineering, sports science, defense, physical therapy",
        "Vrishabha":"commerce, arts, agriculture, banking, architecture",
        "Mithuna":"journalism, languages, IT, mass communication, mathematics",
        "Karka":"nursing, psychology, hospitality, history",
        "Simha":"medicine, management, drama, literature, leadership",
        "Kanya":"medicine, accounting, research, editing, pharmacy",
        "Tula":"law, design, diplomacy, social sciences, fine arts",
        "Vrischika":"research, forensics, psychology, occult sciences",
        "Dhanu":"philosophy, law, education, foreign languages, travel",
        "Makara":"administration, civil services, engineering, finance",
        "Kumbha":"computer science, electronics, astrology, innovation",
        "Meena":"spirituality, medicine, arts, marine, music",
    }
    study_fields = STUDY_FIELDS.get(sign4,"diverse academic fields")

    vidya_yoga = _yoga_present(ctx, ["Saraswati","Vidya","Budhaditya"])
    foreign_edu = "Rahu" in h5_occ or pm.get("Rahu",{}).get("house") in (4,5,9)

    timing = _timing_windows(ctx, [4,5,9], "education")
    remedies = _build_remedies(ctx, ["Mercury"] if m_sc<0 else [], "education")

    return {
        "domain":"Education & Skills","icon":"✦","score":pct,
        "study_fields":study_fields,"vidya_yoga":vidya_yoga,
        "foreign_education":foreign_edu,
        "competitive_success":"Good competitive exam success" if pct>65 else "Focused preparation needed for competitive exams",
        "mercury_position":f"Mercury in {_ordinal(mercury.get('house',1))}H — {mercury.get('strength','')}",
        "dasha_active":dasha_active,"timing":timing,"remedies":remedies,
        "analysis":f"4th/5th houses govern education. Mercury (intellect) in {_ordinal(mercury.get('house',1))} house — {mercury.get('strength','')}. Best study fields: {study_fields}. {('Vidya Yoga present: '+', '.join(vidya_yoga)+' — academic distinction likely.' if vidya_yoga else '')} Foreign education: {'indicated' if foreign_edu else 'less prominent'}.",
    }


# ═══════════════════════════════════════════════════
# DOMAIN 7 — PROPERTY & HOME
# ═══════════════════════════════════════════════════

def analyse_property(ctx: dict) -> dict:
    pm = ctx["planet_map"]
    hl = ctx["house_lords"]

    mars = pm.get("Mars",{}); moon=pm.get("Moon",{}); saturn=pm.get("Saturn",{})
    lord_4 = hl[4]; l4d = pm.get(lord_4,{})
    h4_occ = [p for p,d in pm.items() if d["house"]==4]

    base  = _score_planets_in_houses(ctx, [4,2,12])
    l4s   = _score_house_lord(ctx, 4)
    m_sc  = mars.get("str_score",0)+(2 if mars.get("house") in (4,2) else 0)
    total = base + l4s + m_sc

    dasha_active = _dasha_activates(ctx, [4,12,2])
    pct = _pct(50, total, 8 if dasha_active else 0)

    sign4 = ctx["house_signs"][4]
    PROP_TYPE = {
        "Mesha":"independent house / active environment preferred",
        "Vrishabha":"fertile land, luxurious property, garden",
        "Mithuna":"apartment in busy area, multi-story building",
        "Karka":"near water body, ancestral property",
        "Simha":"large prestigious property, prominent location",
        "Kanya":"clean, hygienic, well-organized living space",
        "Tula":"beautiful, artistically designed home",
        "Vrischika":"old or hidden property, secretive location",
        "Dhanu":"property near temples, open land, hills",
        "Makara":"durable construction, traditional or stone buildings",
        "Kumbha":"modern housing society, tech-enabled home",
        "Meena":"near sea, spiritual property, irregular shape",
    }
    prop_type = PROP_TYPE.get(sign4,"varied property types")

    multiple_props = mars.get("str_score",0)>=2 or (mars.get("house")==4 and "Mars" in h4_occ)
    domestic_happiness = "Moon" in h4_occ or moon.get("house")==4 or moon.get("str_score",0)>=1

    timing = _timing_windows(ctx, [4,2,12], "property")
    remedies = _build_remedies(ctx, ["Mars"] if m_sc<0 else [], "property")

    return {
        "domain":"Property & Home","icon":"⌂","score":pct,
        "property_type":prop_type,"multiple_properties":multiple_props,
        "domestic_happiness":domestic_happiness,
        "vastu":"4th house in earthy signs — vastu compliance highly beneficial" if sign4 in ("Vrishabha","Kanya","Makara") else "Standard vastu principles apply",
        "fourth_lord":f"{lord_4} in {_ordinal(l4d.get('house',0))}H — {l4d.get('strength','')}",
        "mars_position":f"Mars in {_ordinal(mars.get('house',1))}H — {mars.get('strength','')}",
        "dasha_active":dasha_active,"timing":timing,"remedies":remedies,
        "analysis":f"4th house (property) ruled by {lord_4} in {_ordinal(l4d.get('house',1))} house — {l4d.get('strength','')}. Property type: {prop_type}. Mars (real estate karaka) in {_ordinal(mars.get('house',1))} house. {('Multiple properties possible.' if multiple_props else '')} Best purchase window: {timing['best_window']}.",
    }


# ═══════════════════════════════════════════════════
# DOMAIN 8 — CHALLENGES & DOSHA
# ═══════════════════════════════════════════════════

def analyse_challenges(ctx: dict) -> dict:
    pm  = ctx["planet_map"]
    hl  = ctx["house_lords"]

    rahu = pm.get("Rahu",{}); ketu=pm.get("Ketu",{})
    saturn=pm.get("Saturn",{}); mars=pm.get("Mars",{})

    # Kaal Sarp Dosh
    rahu_h = rahu.get("house",1); ketu_h = ketu.get("house",1)
    all_others = [p for p in pm if p not in ("Rahu","Ketu")]
    ks_range = list(range(min(rahu_h,ketu_h), max(rahu_h,ketu_h)+1))
    kaal_sarp = all(pm[p]["house"] in ks_range for p in all_others if p in pm)

    # Mangal Dosh
    mangal = mars.get("house") in (1,4,7,8,12)

    # Shani Dosh (Sade Sati or 8th Saturn)
    moon_sign_idx = RASHI.index(pm.get("Moon",{}).get("sign","Mesha")) if pm.get("Moon",{}).get("sign") in RASHI else 0
    sat_sign_idx  = RASHI.index(saturn.get("sign","Mesha")) if saturn.get("sign") in RASHI else 0
    sade_sati = abs(sat_sign_idx - moon_sign_idx) in (0,1,11)

    # Pitru Dosh (Sun afflicted or Ketu in 9th)
    sun = pm.get("Sun",{})
    pitru = sun.get("str_score",0)<0 or ketu.get("house")==9 or (rahu.get("house")==9)

    # Grahan Dosh (Rahu/Ketu with Sun/Moon)
    grahan_planets = []
    for lum in ["Sun","Moon"]:
        lum_h = pm.get(lum,{}).get("house",0)
        if lum_h in (rahu.get("house",0), ketu.get("house",0)):
            grahan_planets.append(lum)
    grahan = len(grahan_planets) > 0

    doshas_found = []
    if kaal_sarp: doshas_found.append({"name":"Kaal Sarp Dosh","severity":"High","desc":"All planets hemmed between Rahu and Ketu — intense karmic patterns, obstacles followed by sudden rises."})
    if mangal:    doshas_found.append({"name":"Mangal Dosh","severity":"Moderate","desc":f"Mars in {_ordinal(mars.get('house',1))} house — relationship friction, energy imbalance. Match with similar chart."})
    if sade_sati: doshas_found.append({"name":"Shani Sade Sati","severity":"Moderate","desc":"Saturn transiting near Moon sign — 7.5-year karmic cleansing phase."})
    if pitru:     doshas_found.append({"name":"Pitru Dosh","severity":"Moderate","desc":"Ancestral karmic debt — offer tarpan on Amavasya and Pitru Paksha."})
    if grahan:    doshas_found.append({"name":"Grahan Dosh","severity":"Moderate" if len(grahan_planets)==1 else "High","desc":f"Rahu/Ketu eclipsing {', '.join(grahan_planets)} — emotional or identity challenges."})

    # Enemy / legal troubles (6th house affliction)
    h6_malefics = [p for p in ["Saturn","Mars","Rahu"] if pm.get(p,{}).get("house")==6]
    legal_risk = len(h6_malefics)>0

    total_severity = len(doshas_found)
    pct = max(10, min(90, 80 - total_severity*15))

    remedies = _build_remedies(ctx,
        (["Rahu","Ketu"] if kaal_sarp else []) +
        (["Mars"] if mangal else []) +
        (["Saturn"] if sade_sati else []) +
        (["Sun"] if pitru else []),
        "challenges")

    return {
        "domain":"Challenges & Doshas","icon":"⚡","score":pct,
        "kaal_sarp":kaal_sarp,"mangal_dosh":mangal,"sade_sati":sade_sati,
        "pitru_dosh":pitru,"grahan_dosh":grahan,
        "doshas_found":doshas_found,"dosha_count":total_severity,
        "legal_risk":legal_risk,
        "legal_txt":"6th house affliction — litigation or conflict with authority possible. Avoid legal disputes." if legal_risk else "No strong legal trouble indicators.",
        "remedies":remedies,
        "analysis":_challenges_narrative(doshas_found),
    }


def _challenges_narrative(doshas_found):
    if not doshas_found:
        return "No major doshas detected — chart is relatively clean and free from major planetary afflictions."
    names = ", ".join([d["name"] for d in doshas_found])
    return f"{len(doshas_found)} dosha(s) detected: {names}. Appropriate remedies can significantly mitigate these effects. Consult an experienced Vedic astrologer for personalised rituals."


# ═══════════════════════════════════════════════════
# DOMAIN 9 — TRAVEL & FOREIGN
# ═══════════════════════════════════════════════════

def analyse_travel(ctx: dict) -> dict:
    pm = ctx["planet_map"]
    hl = ctx["house_lords"]

    rahu=pm.get("Rahu",{}); ketu=pm.get("Ketu",{}); moon=pm.get("Moon",{})
    lord_12=hl[12]; l12d=pm.get(lord_12,{})
    lord_9=hl[9]; l9d=pm.get(lord_9,{})
    h12_occ=[p for p,d in pm.items() if d["house"]==12]
    h9_occ=[p for p,d in pm.items() if d["house"]==9]

    base  = _score_planets_in_houses(ctx, [12,9,3])
    l12s  = _score_house_lord(ctx, 12)
    r_sc  = 2 if rahu.get("house") in (12,9,3) else 0
    total = base + l12s + r_sc

    dasha_active = _dasha_activates(ctx, [12,9,3])
    pct = _pct(50, total, 8 if dasha_active else 0)

    foreign_strong = rahu.get("house") in (12,9,7,1) or "Rahu" in h12_occ
    visa_ok = lord_9 == "Jupiter" or l9d.get("str_score",0)>=1 or "Jupiter" in h9_occ

    # Direction from 4th house lord
    sign4=ctx["house_signs"][4]
    DIR_MAP={"Mesha":"East","Vrishabha":"South","Mithuna":"North","Karka":"North-West",
             "Simha":"East","Kanya":"South","Tula":"West","Vrischika":"North",
             "Dhanu":"North-East","Makara":"South","Kumbha":"West","Meena":"North-East"}
    direction = DIR_MAP.get(sign4,"Variable direction")

    timing  = _timing_windows(ctx, [12,9,3], "travel")
    remedies= _build_remedies(ctx, ["Rahu"] if not foreign_strong else [], "travel")

    return {
        "domain":"Travel & Foreign","icon":"✈","score":pct,
        "foreign_settlement":foreign_strong,"visa_success":visa_ok,
        "direction":direction,
        "overseas_career":"Strong overseas career potential" if rahu.get("house")==10 else "Domestic career more prominent",
        "twelfth_lord":f"{lord_12} in {_ordinal(l12d.get('house',0))}H — {l12d.get('strength','')}",
        "rahu_position":f"Rahu in {_ordinal(rahu.get('house',1))}H — key foreign indicator",
        "dasha_active":dasha_active,"timing":timing,"remedies":remedies,
        "analysis":f"12th house (foreign lands) ruled by {lord_12} in {_ordinal(l12d.get('house',1))} house. Rahu in {_ordinal(rahu.get('house',1))} house. Foreign settlement: {'strongly indicated' if foreign_strong else 'less prominent'}. Best direction: {direction}. Travel window: {timing['best_window']}.",
    }


# ═══════════════════════════════════════════════════
# DOMAIN 10 — SPIRITUALITY & KARMA
# ═══════════════════════════════════════════════════

def analyse_spirituality(ctx: dict) -> dict:
    pm=ctx["planet_map"]; hl=ctx["house_lords"]

    ketu=pm.get("Ketu",{}); jupiter=pm.get("Jupiter",{}); saturn=pm.get("Saturn",{}); sun=pm.get("Sun",{})
    lord_9=hl[9]; l9d=pm.get(lord_9,{})
    lord_12=hl[12]; l12d=pm.get(lord_12,{})
    h9_occ=[p for p,d in pm.items() if d["house"]==9]
    h12_occ=[p for p,d in pm.items() if d["house"]==12]

    base  = _score_planets_in_houses(ctx, [9,12,1,5])
    l9s   = _score_house_lord(ctx, 9)
    j_sc  = jupiter.get("str_score",0)+(2 if jupiter.get("house") in (9,12,1) else 0)
    k_sc  = 2 if ketu.get("house") in (9,12) else 0
    total = base + l9s + j_sc + k_sc

    dasha_active = _dasha_activates(ctx, [9,12,5])
    pct = _pct(50, total, 8 if dasha_active else 0)

    moksha_yoga = _yoga_present(ctx, ["Moksha","Liberation","Vipreet","Sannyasa"])
    spiritual_inc = ketu.get("house") in (1,5,9,12) or jupiter.get("house") in (9,12)

    # Deity and mantra from Moon nakshatra
    moon_nak = pm.get("Moon",{}).get("nakshatra","")
    DEITY_MAP = {
        "Ashwini":"Ashwini Kumaras","Bharani":"Yama","Krittika":"Agni","Rohini":"Brahma",
        "Mrigashira":"Soma","Ardra":"Rudra","Punarvasu":"Aditi","Pushya":"Brihaspati",
        "Ashlesha":"Nagas","Magha":"Pitrus","Purva Phalguni":"Bhaga","Uttara Phalguni":"Aryaman",
        "Hasta":"Savitri","Chitra":"Vishwakarma","Swati":"Vayu","Vishakha":"Indra/Agni",
        "Anuradha":"Mitra","Jyeshtha":"Indra","Mula":"Nirriti","Purva Ashadha":"Apas",
        "Uttara Ashadha":"Vishwadevas","Shravana":"Vishnu","Dhanishta":"Ashta Vasus",
        "Shatabhisha":"Varuna","Purva Bhadrapada":"Aja Ekapada","Uttara Bhadrapada":"Ahir Budhanya",
        "Revati":"Pusha",
    }
    deity = DEITY_MAP.get(moon_nak,"Lord Vishnu")

    past_karma = f"Ketu in {_ordinal(ketu.get('house',1))} house indicates past-life expertise in {['self-mastery','wealth','communication','home','creativity','service','relationships','occult','dharma','career','gains','liberation'][ketu.get('house',1)-1]}"

    timing  = _timing_windows(ctx, [9,12,5], "spirituality")
    remedies= _build_remedies(ctx, ["Jupiter","Ketu"], "spirituality")

    return {
        "domain":"Spirituality & Karma","icon":"☯","score":pct,
        "spiritual_inclination":spiritual_inc,"moksha_yoga":moksha_yoga,
        "deity":deity,"past_karma":past_karma,
        "dharma_path":f"9th house in {ctx['house_signs'][9]} — dharma expressed through {['individuality','sensory service','communication','nurturing','leadership','service','balance','depth','wisdom','discipline','innovation','surrender'][RASHI.index(ctx['house_signs'][9]) if ctx['house_signs'][9] in RASHI else 0]}",
        "ninth_lord":f"{lord_9} in {_ordinal(l9d.get('house',0))}H — {l9d.get('strength','')}",
        "ketu_position":f"Ketu in {_ordinal(ketu.get('house',1))}H",
        "dasha_active":dasha_active,"timing":timing,"remedies":remedies,
        "analysis":f"9th house (dharma/spirituality) ruled by {lord_9} in {_ordinal(l9d.get('house',1))} house — {l9d.get('strength','')}. {'Strong spiritual inclination indicated.' if spiritual_inc else 'Spiritual growth comes through material experience.'} {past_karma}. Deity: {deity}.",
    }


# ═══════════════════════════════════════════════════
# MASTER FUNCTION — ALL 10 DOMAINS
# ═══════════════════════════════════════════════════

def analyse_all_domains(chart: dict) -> dict:
    """
    Run all 10 life domain analyses on the given chart.
    chart must be the full output from kundali_engine.
    """
    ctx = _build_chart_context(chart)

    return {
        "lagna":       ctx["lagna"],
        "mahadasha":   ctx["mahadasha"],
        "antardasha":  ctx["antardasha"],
        "domains": {
            "marriage":    analyse_marriage(ctx),
            "career":      analyse_career(ctx),
            "wealth":      analyse_wealth(ctx),
            "health":      analyse_health(ctx),
            "children":    analyse_children(ctx),
            "education":   analyse_education(ctx),
            "property":    analyse_property(ctx),
            "challenges":  analyse_challenges(ctx),
            "travel":      analyse_travel(ctx),
            "spirituality":analyse_spirituality(ctx),
        }
    }

    '''
"""
domain_engine.py — Accurate Vedic Life Domain Engine v2
Implements proper Vedic rules:
  - Functional benefic/malefic per lagna
  - Full Vedic aspects (7th + special Mars/Jupiter/Saturn)
  - Neech Bhanga (debilitation cancellation)
  - Shadbala-inspired house strength (kendra/trikona/upachaya/dusthana)
  - Yoga detection integrated per domain
  - Dasha activation via functional nature
  - Navamsa strength correction
  - Transit overlay (Jupiter/Saturn/Rahu over natal houses)
  - Calibrated scoring (never 10% or 98% without real reason)
"""

import swisseph as swe
from datetime import datetime, timezone

swe.set_ephe_path('.')
swe.set_sid_mode(swe.SIDM_LAHIRI)

# ═══════════════════════════════════════════════════
# CORE TABLES
# ═══════════════════════════════════════════════════

RASHI = ["Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya",
         "Tula","Vrischika","Dhanu","Makara","Kumbha","Meena"]

RASHI_EN = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
            "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
    "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha",
    "Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha",
    "Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
    "Uttara Bhadrapada","Revati",
]

SIGN_LORDS = {
    "Mesha":"Mars","Vrishabha":"Venus","Mithuna":"Mercury","Karka":"Moon",
    "Simha":"Sun","Kanya":"Mercury","Tula":"Venus","Vrischika":"Mars",
    "Dhanu":"Jupiter","Makara":"Saturn","Kumbha":"Saturn","Meena":"Jupiter"
}

# Planet natural nature: +2 benefic, -2 malefic, 0 neutral
NATURAL_NATURE = {
    "Jupiter":2,"Venus":2,"Moon":1,"Mercury":0.5,
    "Sun":0,"Mars":-1,"Saturn":-2,"Rahu":-1,"Ketu":-1
}

# Exaltation/debilitation in Sanskrit sign names
EXALTATION   = dict(Sun="Mesha",Moon="Vrishabha",Mars="Makara",Mercury="Kanya",
                    Jupiter="Karka",Venus="Meena",Saturn="Tula",Rahu="Vrishabha",Ketu="Vrischika")
DEBILITATION = dict(Sun="Tula",Moon="Vrischika",Mars="Karka",Mercury="Meena",
                    Jupiter="Makara",Venus="Kanya",Saturn="Mesha",Rahu="Vrischika",Ketu="Vrishabha")
OWN_SIGNS    = dict(Sun=["Simha"],Moon=["Karka"],Mars=["Mesha","Vrischika"],
                    Mercury=["Mithuna","Kanya"],Jupiter=["Dhanu","Meena"],
                    Venus=["Vrishabha","Tula"],Saturn=["Makara","Kumbha"])

# Neech Bhanga: debilitation cancelled if the dispositor of the debilitated planet
# is in kendra from lagna or Moon, or if the exaltation sign lord is in kendra
NEECH_BHANGA_EXALT_LORDS = {
    "Sun":"Venus","Moon":"Jupiter","Mars":"Saturn",
    "Mercury":"Jupiter","Jupiter":"Mars","Venus":"Saturn","Saturn":"Venus"
}

DASHA_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
DASHA_YEARS = dict(Ketu=7,Venus=20,Sun=6,Moon=10,Mars=7,Rahu=18,Jupiter=16,Saturn=19,Mercury=17)
NAK_DIV     = 360/27

PLANET_IDS = dict(Sun=swe.SUN,Moon=swe.MOON,Mercury=swe.MERCURY,Venus=swe.VENUS,
                  Mars=swe.MARS,Jupiter=swe.JUPITER,Saturn=swe.SATURN,Rahu=swe.TRUE_NODE)

# ═══════════════════════════════════════════════════
# FUNCTIONAL NATURE PER LAGNA
# Lords of 1,5,9 = Functional Benefic
# Lords of 6,8,12 = Functional Malefic
# Lords of Kendra (1,4,7,10) that are natural malefics get yogakaraka status
# ═══════════════════════════════════════════════════

def _functional_nature(lagna_idx: int) -> dict:
    """
    Returns dict {planet: score} where:
      +2 = strong functional benefic (trikona lord)
      +1 = mild functional benefic (kendra lord, yogakaraka)
       0 = neutral
      -1 = mild functional malefic
      -2 = strong functional malefic (8th/12th lord)
    """
    fn = {}
    for h in range(1, 13):
        sign = RASHI[(lagna_idx + h - 1) % 12]
        lord = SIGN_LORDS[sign]
        # A planet can rule two houses — take the better one
        existing = fn.get(lord, 0)
        if h in (1, 5, 9):
            fn[lord] = max(existing, 2)
        elif h == 8:
            fn[lord] = min(existing, -2)
        elif h in (6, 12):
            fn[lord] = min(existing, -1)
        elif h in (4, 7, 10):  # kendra
            if existing == 0:
                fn[lord] = 1
        else:
            if existing == 0:
                fn[lord] = 0

    # Special: if a natural malefic lords both a kendra and trikona → Yogakaraka (+3)
    for h1 in (1, 5, 9):
        lord1 = SIGN_LORDS[RASHI[(lagna_idx + h1 - 1) % 12]]
        for h2 in (4, 7, 10):
            lord2 = SIGN_LORDS[RASHI[(lagna_idx + h2 - 1) % 12]]
            if lord1 == lord2 and NATURAL_NATURE.get(lord1, 0) < 0:
                fn[lord1] = 3  # Yogakaraka

    return fn


def _ordinal(n: int) -> str:
    s = {1:"st",2:"nd",3:"rd"}.get(n if n < 20 else n % 10, "th")
    return f"{n}{s}"


# ═══════════════════════════════════════════════════
# PLANET STRENGTH (multi-layer)
# ═══════════════════════════════════════════════════

def _positional_strength(name: str, sign: str, navamsa: str = "") -> float:
    """
    Returns strength score -3 to +4:
      Exalted in D1: +3
      Own Sign D1:   +2
      Neutral D1:     0
      Debilitated D1: -2 (or -1 if Neech Bhanga)
      D9 exalted adds +1; D9 debilitated subtracts -0.5
    """
    score = 0.0
    if EXALTATION.get(name) == sign:
        score = 3.0
    elif sign in OWN_SIGNS.get(name, []):
        score = 2.0
    elif DEBILITATION.get(name) == sign:
        score = -2.0
    else:
        score = 0.0

    # Navamsa correction
    if navamsa:
        if EXALTATION.get(name) == navamsa:
            score += 1.0
        elif navamsa in OWN_SIGNS.get(name, []):
            score += 0.5
        elif DEBILITATION.get(name) == navamsa:
            score -= 0.5

    return score


def _house_strength(house: int) -> float:
    """
    Shadbala-inspired house placement score:
    Kendra (1,4,7,10): +1.5
    Trikona (5,9): +1.5 (1 is both kendra and trikona)
    Upachaya (3,6,10,11): +0.8 for malefics, neutral for benefics
    Dusthana (6,8,12): -1.0
    2nd, 11th: +0.5
    """
    if house == 1:  return 1.5
    if house in (4, 7, 10): return 1.2
    if house in (5, 9):     return 1.5
    if house in (2, 11):    return 0.5
    if house in (3,):       return 0.2
    if house == 6:          return -0.8
    if house in (8, 12):    return -1.2
    return 0.0


def _retrograde_modifier(name: str, retro: bool, house: int) -> float:
    """
    Retrograde planets are stronger in good houses, weaker in bad houses.
    In classical Vedic astrology retrograde natural benefics in 5,9 are very powerful.
    """
    if not retro: return 0.0
    if name in ("Jupiter","Venus","Mercury") and house in (5,9,1):
        return 0.5
    if name in ("Saturn","Mars") and house in (6,3):
        return 0.3
    return -0.2


def _neech_bhanga(name: str, sign: str, planet_map: dict) -> bool:
    """
    True if the planet's debilitation is cancelled.
    Classical Neech Bhanga conditions:
    1. Lord of the debilitation sign is in kendra from lagna or Moon
    2. The planet that gets exalted in the same sign is in kendra
    3. The debilitated planet is retrograde
    """
    if DEBILITATION.get(name) != sign:
        return False

    # Condition 3: retrograde
    if planet_map.get(name, {}).get("retrograde"):
        return True

    # Condition 1: dispositor of debilitation sign in kendra
    dispositor = SIGN_LORDS[sign]
    disp_house = planet_map.get(dispositor, {}).get("house", 0)
    if disp_house in (1, 4, 7, 10):
        return True

    # Condition 2: exaltation sign lord in kendra
    exalt_lord = NEECH_BHANGA_EXALT_LORDS.get(name)
    if exalt_lord:
        el_house = planet_map.get(exalt_lord, {}).get("house", 0)
        if el_house in (1, 4, 7, 10):
            return True

    return False


def _planet_net_score(name: str, pdata: dict, fn: dict, planet_map: dict) -> float:
    """
    Composite planet strength for domain scoring:
    = natural_nature + positional_strength + house_strength
      + functional_nature + retrograde + neech_bhanga_correction
    """
    sign    = pdata.get("sign", "")
    house   = pdata.get("house", 1)
    retro   = pdata.get("retrograde", False)
    navamsa = pdata.get("navamsa", "")

    pos_str  = _positional_strength(name, sign, navamsa)

    # Neech Bhanga cancels debilitation
    if pos_str == -2.0 and _neech_bhanga(name, sign, planet_map):
        pos_str = 0.0  # treated as neutral after cancellation

    h_str    = _house_strength(house)
    retro_m  = _retrograde_modifier(name, retro, house)
    nat      = NATURAL_NATURE.get(name, 0)
    func     = fn.get(name, 0)

    return nat + pos_str + h_str + retro_m + func * 0.5


# ═══════════════════════════════════════════════════
# VEDIC ASPECTS
# ═══════════════════════════════════════════════════

def _aspected_houses(planet: str, house: int) -> list:
    """Return all houses a planet aspects from given house (Vedic full aspects)."""
    aspects = [((house + 6 - 1) % 12) + 1]  # 7th from house
    if planet == "Mars":
        aspects += [((house + 3 - 1) % 12) + 1, ((house + 7 - 1) % 12) + 1]
    elif planet == "Jupiter":
        aspects += [((house + 4 - 1) % 12) + 1, ((house + 8 - 1) % 12) + 1]
    elif planet == "Saturn":
        aspects += [((house + 2 - 1) % 12) + 1, ((house + 9 - 1) % 12) + 1]
    elif planet in ("Rahu", "Ketu"):
        aspects += [((house + 4 - 1) % 12) + 1, ((house + 8 - 1) % 12) + 1]
    return list(set(aspects))


def _aspect_score_on_house(target_house: int, planet_map: dict, fn: dict) -> float:
    """
    Sum of scores from all planets aspecting target_house.
    Benefics aspecting = positive; malefics aspecting = negative.
    """
    score = 0.0
    for pname, pdata in planet_map.items():
        ph = pdata.get("house", 0)
        if target_house in _aspected_houses(pname, ph):
            # Aspect strength = natural + functional
            nat  = NATURAL_NATURE.get(pname, 0)
            func = fn.get(pname, 0)
            score += (nat + func * 0.4) * 0.6  # aspects are 60% of direct placement
    return score


# ═══════════════════════════════════════════════════
# DASHA ACTIVATION (accurate)
# ═══════════════════════════════════════════════════

def _dasha_quality(dasha_lord: str, key_houses: list, planet_map: dict,
                   house_lords: dict, fn: dict) -> float:
    """
    Returns quality score of a dasha for given key houses:
    +2 if lord is functional benefic AND rules/occupies key house
    +1 if lord occupies key house but mixed nature
    -1 if lord is functional malefic but in good position
    -2 if lord is strong malefic ruling 6/8/12 and activating key house badly
    """
    if not dasha_lord:
        return 0.0

    func_score  = fn.get(dasha_lord, 0)
    pdata       = planet_map.get(dasha_lord, {})
    p_house     = pdata.get("house", 0)
    pos_str     = _positional_strength(dasha_lord, pdata.get("sign",""), pdata.get("navamsa",""))

    # Does dasha lord rule any key house?
    rules_key = any(house_lords.get(h) == dasha_lord for h in key_houses)
    # Does dasha lord occupy a key house?
    occupies_key = p_house in key_houses

    base = func_score + pos_str * 0.3
    if rules_key and occupies_key:
        return base + 2.0
    if rules_key or occupies_key:
        return base + 1.0
    return base * 0.3


# ═══════════════════════════════════════════════════
# CURRENT TRANSIT ANALYSIS
# ═══════════════════════════════════════════════════

def _get_transits(lagna_idx: int) -> dict:
    """Current transit positions of slow planets relative to natal lagna."""
    FLAG = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    now  = datetime.now(timezone.utc)
    jd   = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60)
    result = {}
    for pname, pid in PLANET_IDS.items():
        lon = swe.calc_ut(jd, pid, FLAG)[0][0] % 360
        if pname == "Rahu":
            ketu_lon = (lon+180)%360
            result["Ketu"] = {"sign":RASHI[int(ketu_lon/30)], "house":((int(ketu_lon/30)-lagna_idx)%12)+1}
        result[pname] = {"sign":RASHI[int(lon/30)], "house":((int(lon/30)-lagna_idx)%12)+1}
    return result


def _transit_score(key_houses: list, transits: dict, fn: dict) -> float:
    """
    Score current transits over key houses.
    Jupiter transiting key house = strong positive.
    Saturn transiting key house = tests (negative).
    Rahu/Ketu = mixed.
    """
    score = 0.0
    for pname, tdata in transits.items():
        if tdata["house"] in key_houses:
            nat  = NATURAL_NATURE.get(pname, 0)
            func = fn.get(pname, 0)
            # Transits are weaker than natal — 40% weight
            score += (nat + func * 0.3) * 0.4
    # Also check aspects from transit planets onto key houses
    for pname, tdata in transits.items():
        for kh in key_houses:
            if kh in _aspected_houses(pname, tdata["house"]):
                nat  = NATURAL_NATURE.get(pname, 0)
                score += nat * 0.2
    return score


# ═══════════════════════════════════════════════════
# YOGA DETECTION (domain-specific)
# ═══════════════════════════════════════════════════

def _detect_yogas(planet_map: dict, house_lords: dict, lagna_idx: int) -> list:
    """Detect all major yogas from the chart. Returns list of active yoga names."""
    yogas = []
    ph = {n: d["house"] for n,d in planet_map.items()}

    # Gajakesari
    moon_h = ph.get("Moon",0); jup_h = ph.get("Jupiter",0)
    if moon_h and jup_h and (jup_h - moon_h) % 12 in (0,3,6,9):
        yogas.append("Gajakesari Yoga")

    # Budhaditya
    for h, plist in _planets_by_house(planet_map).items():
        if "Sun" in plist and "Mercury" in plist:
            yogas.append("Budhaditya Yoga")

    # Raj Yoga: kendra lord + trikona lord conjunct or exchange
    kendra_lords = {house_lords.get(h) for h in (1,4,7,10)}
    trikona_lords = {house_lords.get(h) for h in (1,5,9)}
    kendra_lords.discard(None); trikona_lords.discard(None)
    for kl in kendra_lords:
        if kl in trikona_lords:
            yogas.append("Raj Yoga")
        for tl in trikona_lords:
            if kl != tl and ph.get(kl) == ph.get(tl):  # conjunction
                yogas.append("Raj Yoga")

    # Dhana Yoga: 2nd and 11th lords together
    l2 = house_lords.get(2); l11 = house_lords.get(11)
    if l2 and l11 and l2 != l11 and ph.get(l2) == ph.get(l11):
        yogas.append("Dhana Yoga")
    if l2 and l11 and ph.get(l2) in (2,11) and ph.get(l11) in (2,11):
        yogas.append("Dhana Yoga")

    # Lakshmi Yoga: Venus strong + 9th lord in own sign or exalted
    l9 = house_lords.get(9)
    v_sign = planet_map.get("Venus",{}).get("sign","")
    l9_sign = planet_map.get(l9,{}).get("sign","") if l9 else ""
    if (v_sign in OWN_SIGNS.get("Venus",[]) or EXALTATION.get("Venus")==v_sign) and \
       (l9_sign in OWN_SIGNS.get(l9,[]) or EXALTATION.get(l9)==l9_sign):
        yogas.append("Lakshmi Yoga")

    # Vipreet Raj Yoga: dusthana lords in dusthanas
    for h in (6,8,12):
        lord = house_lords.get(h)
        if lord and ph.get(lord,0) in (6,8,12):
            yogas.append("Vipreet Raj Yoga")

    # Hamsa Yoga: Jupiter in kendra in own/exalted sign
    if jup_h in (1,4,7,10):
        j_sign = planet_map.get("Jupiter",{}).get("sign","")
        if j_sign in OWN_SIGNS.get("Jupiter",[]) or EXALTATION.get("Jupiter")==j_sign:
            yogas.append("Hamsa Yoga")

    # Malavya Yoga: Venus in kendra in own/exalted sign
    v_house = ph.get("Venus",0)
    if v_house in (1,4,7,10):
        if v_sign in OWN_SIGNS.get("Venus",[]) or EXALTATION.get("Venus")==v_sign:
            yogas.append("Malavya Yoga")

    # Sasa Yoga: Saturn in kendra in own/exalted sign
    sat_h = ph.get("Saturn",0)
    s_sign = planet_map.get("Saturn",{}).get("sign","")
    if sat_h in (1,4,7,10) and (s_sign in OWN_SIGNS.get("Saturn",[]) or EXALTATION.get("Saturn")==s_sign):
        yogas.append("Sasa Yoga")

    # Kalatra Yoga: Venus or 7th lord strong and in 1st/7th
    l7 = house_lords.get(7)
    l7_house = ph.get(l7,0) if l7 else 0
    if (l7_house in (1,7) or v_house in (1,7)):
        l7_sign = planet_map.get(l7,{}).get("sign","") if l7 else ""
        if l7_sign in OWN_SIGNS.get(l7,[]) if l7 else False or EXALTATION.get(l7)==l7_sign:
            yogas.append("Kalatra Yoga")

    # Mangal Dosh
    mars_h = ph.get("Mars",0)
    if mars_h in (1,4,7,8,12):
        yogas.append("Mangal Dosh")

    # Kaal Sarp Dosh
    rahu_h = ph.get("Rahu",0); ketu_h = ph.get("Ketu",0)
    if rahu_h and ketu_h:
        lo,hi = min(rahu_h,ketu_h), max(rahu_h,ketu_h)
        others_in_range = all(planet_map[p]["house"] in range(lo,hi+1)
                              for p in planet_map if p not in ("Rahu","Ketu"))
        if others_in_range:
            yogas.append("Kaal Sarp Dosh")

    # Pitru Dosh
    sun_sign = planet_map.get("Sun",{}).get("sign","")
    sun_str  = _positional_strength("Sun",sun_sign)
    if sun_str < -1 or ph.get("Ketu",0)==9 or ph.get("Rahu",0)==9:
        yogas.append("Pitru Dosh")

    # Grahan Dosh
    for lum in ("Sun","Moon"):
        lum_h = ph.get(lum,0)
        if lum_h in (rahu_h, ketu_h):
            yogas.append(f"Grahan Dosh ({lum})")

    # Putra Dosh
    l5 = house_lords.get(5)
    l5_sign = planet_map.get(l5,{}).get("sign","") if l5 else ""
    j_sign  = planet_map.get("Jupiter",{}).get("sign","")
    j_str   = _positional_strength("Jupiter",j_sign)
    l5_str  = _positional_strength(l5,l5_sign) if l5 else 0
    if j_str <= -1.5 and l5_str <= -1.5:
        yogas.append("Putra Dosh")

    # Saraswati Yoga: Mercury/Jupiter/Venus all in 1,2,4,5,7,9,10,11
    good_houses = (1,2,4,5,7,9,10,11)
    if all(ph.get(p,0) in good_houses for p in ("Mercury","Jupiter","Venus")):
        yogas.append("Saraswati Yoga")

    return list(set(yogas))


def _planets_by_house(planet_map: dict) -> dict:
    pbh = {i:[] for i in range(1,13)}
    for pname, pdata in planet_map.items():
        h = pdata.get("house",1)
        if 1<=h<=12:
            pbh[h].append(pname)
    return pbh


# ═══════════════════════════════════════════════════
# CHART CONTEXT BUILDER
# ═══════════════════════════════════════════════════

def _build_ctx(chart: dict) -> dict:
    """Build rich context from kundali chart output."""
    lagna    = chart.get("lagna","Mesha")
    lagna_idx= RASHI.index(lagna) if lagna in RASHI else 0

    # House lords
    house_lords = {}
    house_signs = {}
    for h in range(1,13):
        sign = RASHI[(lagna_idx + h - 1) % 12]
        house_lords[h] = SIGN_LORDS[sign]
        house_signs[h] = sign

    # Planet map
    planet_map = {}
    for p in chart.get("planets",[]):
        name = p.get("name")
        if not name: continue
        sign  = p.get("sign","Mesha")
        house = int(p.get("house", ((RASHI.index(sign) if sign in RASHI else 0) - lagna_idx) % 12 + 1))
        planet_map[name] = {
            "sign":      sign,
            "house":     house,
            "retrograde":bool(p.get("retrograde",False)),
            "nakshatra": p.get("nakshatra",""),
            "navamsa":   p.get("navamsa",""),
            "strength":  p.get("strength","Neutral"),
        }

    # Ketu from Rahu if missing
    if "Rahu" in planet_map and "Ketu" not in planet_map:
        r_sidx = RASHI.index(planet_map["Rahu"]["sign"]) if planet_map["Rahu"]["sign"] in RASHI else 0
        k_sign = RASHI[(r_sidx+6)%12]
        k_house= ((r_sidx+6-lagna_idx)%12)+1
        planet_map["Ketu"] = {"sign":k_sign,"house":k_house,"retrograde":True,"nakshatra":"","navamsa":"","strength":"Neutral"}

    # Functional nature
    fn = _functional_nature(lagna_idx)

    # Pre-compute net score per planet
    net_scores = {n: _planet_net_score(n, d, fn, planet_map) for n,d in planet_map.items()}

    # Detect all yogas
    yogas = _detect_yogas(planet_map, house_lords, lagna_idx)

    # Current transits
    transits = _get_transits(lagna_idx)

    # Dasha
    mahadasha = chart.get("mahadasha","")
    antardasha= chart.get("antardasha","")

    return {
        "lagna":       lagna,
        "lagna_idx":   lagna_idx,
        "planet_map":  planet_map,
        "house_lords": house_lords,
        "house_signs": house_signs,
        "fn":          fn,
        "net_scores":  net_scores,
        "yogas":       yogas,
        "transits":    transits,
        "mahadasha":   mahadasha,
        "antardasha":  antardasha,
        "pbh":         _planets_by_house(planet_map),
    }


# ═══════════════════════════════════════════════════
# DOMAIN SCORE ENGINE
# ═══════════════════════════════════════════════════

def _domain_score(ctx: dict, primary_houses: list, karaka: str = None,
                  secondary_houses: list = None) -> dict:
    """
    Compute domain score (0-100) using:
    1. Direct occupation of primary houses by planets (with net scores)
    2. Aspects onto primary houses
    3. House lord strength
    4. Karaka planet strength
    5. Dasha activation quality
    6. Transit overlay
    Returns dict with 'score', 'dasha_active', 'dasha_quality', 'transit_score'
    """
    secondary_houses = secondary_houses or []
    pm  = ctx["planet_map"]
    hl  = ctx["house_lords"]
    fn  = ctx["fn"]
    ns  = ctx["net_scores"]
    tr  = ctx["transits"]
    md  = ctx["mahadasha"]
    ad  = ctx["antardasha"]

    # 1. Occupation score
    occ_score = 0.0
    for h in primary_houses:
        planets_in_h = [p for p,d in pm.items() if d["house"]==h]
        for p in planets_in_h:
            occ_score += ns.get(p, 0)
        # Aspect score on this house
        occ_score += _aspect_score_on_house(h, pm, fn)

    for h in secondary_houses:
        planets_in_h = [p for p,d in pm.items() if d["house"]==h]
        for p in planets_in_h:
            occ_score += ns.get(p, 0) * 0.5
        occ_score += _aspect_score_on_house(h, pm, fn) * 0.4

    # 2. House lord strength
    lord_score = 0.0
    for h in primary_houses:
        lord = hl.get(h)
        if lord and lord in ns:
            lord_score += ns[lord] * 0.8
    for h in secondary_houses:
        lord = hl.get(h)
        if lord and lord in ns:
            lord_score += ns[lord] * 0.4

    # 3. Karaka strength
    karaka_score = 0.0
    if karaka and karaka in ns:
        karaka_score = ns[karaka] * 1.2

    # 4. Dasha activation
    dq_md = _dasha_quality(md, primary_houses, pm, hl, fn)
    dq_ad = _dasha_quality(ad, primary_houses, pm, hl, fn)
    dasha_score  = dq_md * 0.7 + dq_ad * 0.5
    dasha_active = abs(dq_md) > 0.5 or abs(dq_ad) > 0.5

    # 5. Transit score
    transit_score = _transit_score(primary_houses, tr, fn)

    # 6. Total raw score
    raw = occ_score + lord_score + karaka_score + dasha_score * 0.4 + transit_score * 0.3

    # Calibrate to 20-85 range (extreme values only on exceptional charts)
    # Base = 50, each unit of raw ≈ 4 points
    calibrated = 50 + raw * 4
    calibrated = max(15, min(88, calibrated))

    return {
        "score":         int(round(calibrated)),
        "raw":           round(raw, 2),
        "dasha_active":  dasha_active,
        "dasha_quality": round(dq_md + dq_ad, 2),
        "transit_score": round(transit_score, 2),
        "occ_score":     round(occ_score, 2),
        "lord_score":    round(lord_score, 2),
        "karaka_score":  round(karaka_score, 2),
    }


# ═══════════════════════════════════════════════════
# SHARED UTILITIES
# ═══════════════════════════════════════════════════

PLANET_REMEDIES = {
    "Sun":     dict(gem="Ruby (Manik)", mantra="Om Suryaya Namah (108×)", fast="Sunday", donate="Wheat, jaggery, copper"),
    "Moon":    dict(gem="Pearl (Moti)", mantra="Om Chandraya Namah (108×)", fast="Monday", donate="Rice, white cloth, milk, silver"),
    "Mars":    dict(gem="Red Coral (Moonga)", mantra="Om Mangalaya Namah (108×)", fast="Tuesday", donate="Red lentils, copper, red cloth"),
    "Mercury": dict(gem="Emerald (Panna)", mantra="Om Budhaya Namah (108×)", fast="Wednesday", donate="Green gram, green cloth, books"),
    "Jupiter": dict(gem="Yellow Sapphire (Pukhraj)", mantra="Om Gurave Namah (108×)", fast="Thursday", donate="Yellow items, gold, turmeric, chana dal"),
    "Venus":   dict(gem="Diamond / White Sapphire", mantra="Om Shukraya Namah (108×)", fast="Friday", donate="White items, perfume, silver, rice"),
    "Saturn":  dict(gem="Blue Sapphire (Neelam)", mantra="Om Shanicharaya Namah (108×)", fast="Saturday", donate="Sesame, iron, black urad dal, oil"),
    "Rahu":    dict(gem="Hessonite (Gomed)", mantra="Om Rahave Namah (108×)", fast="Saturday", donate="Coconut, blue/black items, blanket"),
    "Ketu":    dict(gem="Cat's Eye (Lehsunia)", mantra="Om Ketave Namah (108×)", fast="Tuesday", donate="Multi-colored cloth, sesame, blanket"),
}

DOMAIN_RITUALS = {
    "marriage":    "Swayamvara Parvati puja for marriage. Worship Katyayani Devi during Navratri. Recite Mangalashtak.",
    "career":      "Surya Namaskar at sunrise. Offer water to Sun chanting Gayatri Mantra. Worship Lord Rama on Ram Navami.",
    "wealth":      "Lakshmi puja on Fridays with lotus flowers. Light ghee lamp facing East. Recite Shri Sukta.",
    "health":      "Maha Mrityunjaya Mantra 108× daily. Worship Lord Dhanvantari. Observe Ekadashi fast.",
    "children":    "Santana Gopala mantra 108×. Worship Lord Krishna on Janmashtami. Offer milk to Shivalinga.",
    "education":   "Saraswati puja on Vasant Panchami. Keep workspace clean. Recite Saraswati Vandana before study.",
    "property":    "Vastu puja before purchase. Worship Bhumi Devi. Offer flowers to Ganesha before construction.",
    "challenges":  "Hanuman Chalisa on Tuesdays and Saturdays. Navagraha homa. Offer sesame to Saturn on Saturday.",
    "travel":      "Worship Kaal Bhairav before travel. Offer coconut and blue flowers to Rahu. Carry Ganesha yantra.",
    "spirituality":"Daily Sandhyavandanam. Guru sewa and scriptural study. Meditate at Brahma Muhurat (4-6 AM).",
}

def _build_remedies(ctx: dict, key_planets: list, domain: str) -> dict:
    pm = ctx["planet_map"]; fn = ctx["fn"]; ns = ctx["net_scores"]

    # Find genuinely weak planets — negative net score
    weak_planets = sorted(
        [(p, ns.get(p, 0)) for p in key_planets if p in pm],
        key=lambda x: x[1]
    )[:2]  # worst 2

    planet_remedies = []
    for p, score in weak_planets:
        r = PLANET_REMEDIES.get(p, {})
        if r:
            planet_remedies.append({
                "planet":  p,
                "score":   round(score, 1),
                "gem":     r["gem"],
                "mantra":  r["mantra"],
                "fast":    r["fast"],
                "donate":  r["donate"],
            })

    return {
        "planet_remedies": planet_remedies,
        "ritual":          DOMAIN_RITUALS.get(domain, "Perform Navagraha homa for all-round benefit."),
    }


def _timing(ctx: dict, key_houses: list, event: str) -> dict:
    pm  = ctx["planet_map"]; hl  = ctx["house_lords"]
    fn  = ctx["fn"]; tr  = ctx["transits"]
    md  = ctx["mahadasha"]; ad  = ctx["antardasha"]
    now = datetime.now().year

    # Dasha quality for this domain
    dq_md = _dasha_quality(md, key_houses, pm, hl, fn)
    dq_ad = _dasha_quality(ad, key_houses, pm, hl, fn)
    t_sc  = _transit_score(key_houses, tr, fn)

    jup_house = tr.get("Jupiter",{}).get("house",1)
    sat_house = tr.get("Saturn",{}).get("house",1)
    jup_to_key = min([(h - jup_house) % 12 for h in key_houses], default=12)
    sat_to_key = min([(h - sat_house) % 12 for h in key_houses], default=12)

    if dq_md > 1.0 and t_sc > 0:
        window = f"🟢 Now — {now+2} (Dasha + Jupiter aligned)"
        conf   = "High"
    elif dq_md > 0.5:
        window = f"🟡 Current dasha period ({md}/{ad}) — watch transits"
        conf   = "Moderate"
    elif jup_to_key <= 2:
        window = f"🟡 {now + jup_to_key}–{now + jup_to_key + 2} (Jupiter entering key house)"
        conf   = "Moderate"
    elif jup_to_key <= 5:
        window = f"🔵 ~{now + jup_to_key} (Jupiter transit in ~{jup_to_key} years)"
        conf   = "Approximate"
    else:
        window = f"🔵 Wait for supportive dasha and Jupiter transit"
        conf   = "Long-term"

    if sat_to_key <= 1:
        challenge = f"Saturn in key house now — delays and tests until ~{now+2}. Patience and persistence needed."
    elif sat_to_key <= 3:
        challenge = f"Saturn approaches key house ~{now + sat_to_key} — plan finances and health carefully."
    else:
        challenge = "No immediate Saturn pressure. Stay consistent in efforts."

    return {
        "best_window": window,
        "confidence":  conf,
        "challenge":   challenge,
        "dasha_quality": round(dq_md + dq_ad, 1),
        "transit_score": round(t_sc, 1),
    }


def _house_lord_str(ctx: dict, house: int) -> str:
    lord = ctx["house_lords"].get(house,"")
    pdata= ctx["planet_map"].get(lord,{})
    h    = pdata.get("house",0)
    s    = pdata.get("strength","")
    ns   = round(ctx["net_scores"].get(lord,0),1)
    return f"{lord} in {_ordinal(h)}H ({s}, net {ns:+.1f})"


# ═══════════════════════════════════════════════════
# DOMAIN 1 — MARRIAGE
# ═══════════════════════════════════════════════════

def _marriage(ctx: dict) -> dict:
    pm=ctx["planet_map"]; hl=ctx["house_lords"]; fn=ctx["fn"]; ns=ctx["net_scores"]; yogas=ctx["yogas"]

    result = _domain_score(ctx, [7,2], karaka="Venus", secondary_houses=[5,8,11])
    sc = result["score"]

    venus=pm.get("Venus",{}); mars=pm.get("Mars",{}); jupiter=pm.get("Jupiter",{})
    h7_planets = [p for p,d in pm.items() if d["house"]==7]
    h5_planets = [p for p,d in pm.items() if d["house"]==5]
    lord_7     = hl[7]; l7d=pm.get(lord_7,{})

    # Marriage type
    venus_in_5  = venus.get("house")==5
    venus_in_7  = venus.get("house")==7
    rahu_in_7   = "Rahu" in h7_planets
    jup_in_7    = "Jupiter" in h7_planets
    moon_in_5   = pm.get("Moon",{}).get("house")==5

    if (venus_in_5 or moon_in_5) and ns.get("Venus",0)>0:
        mtype = "Love marriage strongly indicated — Venus/Moon activates 5th house of romance"
    elif rahu_in_7:
        mtype = "Love or inter-caste/inter-cultural marriage — Rahu in 7th breaks conventions"
    elif jup_in_7 and fn.get("Jupiter",0)>=0:
        mtype = "Arranged marriage — Jupiter in 7th brings traditional, auspicious union"
    elif fn.get(lord_7,0) >= 1:
        mtype = "Arranged marriage favoured — 7th lord is functional benefic"
    elif venus_in_7:
        mtype = "Love or love-cum-arranged marriage — Venus directly in 7th"
    else:
        mtype = "Arranged marriage — 7th house supports traditional matchmaking"

    # Partner sign & traits
    sign7 = ctx["house_signs"][7]
    PARTNER = {
        "Mesha":"dynamic, self-driven, competitive, impulsive but honest",
        "Vrishabha":"stable, sensual, patient, artistic, possessive",
        "Mithuna":"witty, communicative, adaptable, dual-natured, intelligent",
        "Karka":"caring, emotional, traditional, protective, moody",
        "Simha":"confident, generous, proud, dramatic, needs respect",
        "Kanya":"analytical, practical, health-focused, perfectionist",
        "Tula":"charming, diplomatic, balanced, beauty-conscious, fair",
        "Vrischika":"intense, loyal, secretive, transformative, passionate",
        "Dhanu":"optimistic, adventurous, honest, philosophical, freedom-loving",
        "Makara":"disciplined, ambitious, serious, reliable, traditional",
        "Kumbha":"independent, humanitarian, unconventional, intellectual",
        "Meena":"empathetic, spiritual, artistic, compassionate, dreamy",
    }
    traits = PARTNER.get(sign7,"dignified and balanced")
    if h7_planets:
        mods = {"Jupiter":"wise and spiritual","Venus":"charming and romantic",
                "Saturn":"mature and older/serious","Mars":"energetic and assertive",
                "Mercury":"articulate and clever","Moon":"nurturing and sensitive",
                "Sun":"confident and prominent","Rahu":"from different background"}
        extra = [mods[p] for p in h7_planets if p in mods]
        if extra: traits += " — " + ", ".join(extra)

    # Mangal Dosh (accurate: 1,2,4,7,8,12 — some classical schools include 2nd)
    mars_h = mars.get("house",0)
    mangal = mars_h in (1,2,4,7,8,12)
    mangal_cancelled = mangal and (
        pm.get("Jupiter",{}).get("house")==7 or
        mars.get("sign") in OWN_SIGNS.get("Mars",[]) or
        EXALTATION.get("Mars")==mars.get("sign","") or
        ns.get("Mars",0) >= 2.0
    )
    if mangal and not mangal_cancelled:
        mangal_txt = f"⚠ Mars in {_ordinal(mars_h)}H — Mangal Dosh present. Match with partner of similar chart pattern."
    elif mangal and mangal_cancelled:
        mangal_txt = f"Mars in {_ordinal(mars_h)}H — Mangal Dosh present but cancelled (Mars strong/Jupiter aspects 7th)"
    else:
        mangal_txt = "✓ No Mangal Dosh"

    # Active yogas for marriage
    m_yogas = [y for y in yogas if any(k in y for k in ("Kalatra","Malavya","Hamsa","Raj"))]

    # Second marriage
    h8_lord = hl[8]; h8_d = pm.get(h8_lord,{})
    second_marriage = "Some indicators for second marriage — 8th lord connects to 7th" \
        if h8_d.get("house") in (7,2,1) or "Rahu" in h7_planets \
        else "No strong second marriage indicators"

    remedies = _build_remedies(ctx, ["Venus", lord_7, "Jupiter"], "marriage")
    timing   = _timing(ctx, [7,5,2], "marriage")

    # Narrative
    v_h=venus.get("house",0); v_s=venus.get("sign",""); v_ns=round(ns.get("Venus",0),1)
    parts=[
        f"Your 7th house of marriage falls in {sign7} ({RASHI_EN[RASHI.index(sign7)] if sign7 in RASHI else sign7}), ruled by {lord_7} placed in {_ordinal(l7d.get('house',1))} house — net strength {round(ns.get(lord_7,0),1):+.1f}.",
        f"{mtype}.",
        f"Venus (karaka of marriage) in {_ordinal(v_h)}H {v_s} with net strength {v_ns:+.1f} — {'strong capacity for love and harmony' if v_ns>=1 else 'needs strengthening through remedies' if v_ns<=-1 else 'moderate relationship potential'}.",
        f"Your partner is likely to be {traits}.",
    ]
    if m_yogas:
        parts.append(f"Auspicious marriage yogas active: {', '.join(m_yogas)}.")
    parts.append(f"Optimal timing: {timing['best_window']}.")

    return {
        "domain":"Marriage & Relationships","icon":"♥","score":sc,
        "marriage_type":mtype,"partner_traits":traits,
        "partner_sign":f"{sign7} ({RASHI_EN[RASHI.index(sign7)] if sign7 in RASHI else sign7})",
        "mangal_dosh":mangal and not mangal_cancelled,
        "mangal_dosh_txt":mangal_txt,
        "mangal_cancelled":mangal_cancelled,
        "active_yogas":m_yogas,"second_marriage":second_marriage,
        "intimacy":"Strong physical chemistry — Mars/Venus influence 8th" if "Mars" in [p for p,d in pm.items() if d["house"]==8] else "Emotional & spiritual connection dominant",
        "venus_position":f"Venus in {_ordinal(v_h)}H {v_s} (net {v_ns:+.1f})",
        "seventh_lord":_house_lord_str(ctx,7),
        "h7_planets":h7_planets,
        "dasha_active":result["dasha_active"],
        "timing":timing,"remedies":remedies,
        "analysis":" ".join(parts),
        "_scoring":result,
    }


# ═══════════════════════════════════════════════════
# DOMAIN 2 — CAREER
# ═══════════════════════════════════════════════════

def _career(ctx: dict) -> dict:
    pm=ctx["planet_map"]; hl=ctx["house_lords"]; fn=ctx["fn"]; ns=ctx["net_scores"]; yogas=ctx["yogas"]

    result = _domain_score(ctx, [10,6], karaka="Sun", secondary_houses=[11,9,3])
    sc = result["score"]

    sun=pm.get("Sun",{}); saturn=pm.get("Saturn",{}); mars=pm.get("Mars",{})
    mercury=pm.get("Mercury",{}); jupiter=pm.get("Jupiter",{})
    h10_planets=[p for p,d in pm.items() if d["house"]==10]
    lord_10=hl[10]; l10d=pm.get(lord_10,{})

    sign10=ctx["house_signs"][10]
    FIELDS = {
        "Mesha":"engineering, military, defence, sports, surgery, athletics",
        "Vrishabha":"banking, finance, agriculture, arts, luxury goods, music",
        "Mithuna":"journalism, IT, marketing, media, teaching, trading, writing",
        "Karka":"real estate, hospitality, catering, social work, nursing, history",
        "Simha":"leadership, politics, medicine, management, entertainment, administration",
        "Kanya":"accounting, medicine, research, editing, data analysis, pharmacy",
        "Tula":"law, diplomacy, design, fashion, HR, counselling, mediation",
        "Vrischika":"research, intelligence, psychology, occult, mining, forensics",
        "Dhanu":"education, law, philosophy, export-import, travel, consulting",
        "Makara":"civil services, engineering, construction, government, corporates",
        "Kumbha":"technology, science, aviation, astrology, NGO, electronics",
        "Meena":"spirituality, arts, medicine, marine, photography, charity",
    }
    best_fields = FIELDS.get(sign10,"diverse professional domains")

    # Sector
    sun_strong = ns.get("Sun",0)>=1 or sun.get("house") in (1,9,10)
    if "Sun" in h10_planets and sun_strong:
        sector="Government / IAS / Politics / Authority roles"
    elif "Saturn" in h10_planets and ns.get("Saturn",0)>=0:
        sector="Corporate / Technical / Service sector / Engineering"
    elif "Mercury" in h10_planets:
        sector="Communication / IT / Business / Finance / Writing"
    elif "Jupiter" in h10_planets and ns.get("Jupiter",0)>=0:
        sector="Teaching / Law / Finance / Consulting / Spiritual roles"
    elif "Mars" in h10_planets:
        sector="Military / Police / Engineering / Surgery / Sports"
    elif fn.get(lord_10,0)>=2:
        sector=f"Prominent career path — 10th lord {lord_10} is a functional benefic"
    else:
        sector="Multiple career paths viable — assess strongest house/planet"

    c_yogas=[y for y in yogas if any(k in y for k in ("Raj","Hamsa","Sasa","Budhaditya","Vipreet"))]

    # Business vs job
    l7 = hl[7]; l7_ns = ns.get(l7,0)
    if "Mercury" in h10_planets or (mercury.get("house")==10) or l7_ns>=1.5:
        bvj="Business strongly favoured — Mercury or strong 7th lord"
    elif "Saturn" in h10_planets or saturn.get("house")==10:
        bvj="Service/Job preferred — Saturn in 10th brings steady employment"
    else:
        bvj="Both viable — compare 7th (business) and 10th (service) house strengths"

    # Foreign
    rahu=pm.get("Rahu",{}); rahu_h=rahu.get("house",0)
    foreign="Strong overseas career potential — Rahu aspects/occupies career houses" if rahu_h in (10,9,12) else "Domestic career more prominent unless Rahu activated by Dasha"

    remedies=_build_remedies(ctx,["Sun",lord_10,"Mercury"],"career")
    timing=_timing(ctx,[10,6,11],"career")

    parts=[
        f"10th house in {sign10} ruled by {lord_10} (in {_ordinal(l10d.get('house',1))}H, net {round(ns.get(lord_10,0),1):+.1f}).",
        f"Career direction: {sector}.",
        f"Best professional fields: {best_fields}.",
    ]
    if c_yogas: parts.append(f"Career-boosting yogas: {', '.join(c_yogas)}.")
    parts.append(f"Optimal window: {timing['best_window']}.")

    return {
        "domain":"Career & Profession","icon":"★","score":sc,
        "sector":sector,"best_fields":best_fields,
        "tenth_lord":_house_lord_str(ctx,10),"h10_planets":h10_planets,
        "raj_yogas":c_yogas,"business_vs_job":bvj,"foreign_work":foreign,
        "dasha_active":result["dasha_active"],
        "timing":timing,"remedies":remedies,"analysis":" ".join(parts),
        "_scoring":result,
    }


# ═══════════════════════════════════════════════════
# DOMAIN 3 — WEALTH
# ═══════════════════════════════════════════════════

def _wealth(ctx: dict) -> dict:
    pm=ctx["planet_map"]; hl=ctx["house_lords"]; fn=ctx["fn"]; ns=ctx["net_scores"]; yogas=ctx["yogas"]

    result=_domain_score(ctx,[2,11],karaka="Jupiter",secondary_houses=[5,9])
    sc=result["score"]

    jupiter=pm.get("Jupiter",{}); venus=pm.get("Venus",{})
    h2_pl=[p for p,d in pm.items() if d["house"]==2]
    h11_pl=[p for p,d in pm.items() if d["house"]==11]
    lord_2=hl[2]; lord_11=hl[11]

    sign11=ctx["house_signs"][11]
    SOURCES={
        "Mesha":"initiative, business, real estate, self-employment",
        "Vrishabha":"banking, accumulation, trading, agriculture, luxury",
        "Mithuna":"communication, media, IT, commissions, multiple income streams",
        "Karka":"real estate, food, family business, emotional intelligence monetised",
        "Simha":"government, leadership, speculation, creative industry",
        "Kanya":"service, health, detailed work, analytical professions",
        "Tula":"partnerships, legal, design, negotiations, balanced portfolios",
        "Vrischika":"research, insurance, inheritance, joint ventures",
        "Dhanu":"education, publishing, exports, overseas, consulting",
        "Makara":"professional services, construction, government, slow but steady",
        "Kumbha":"technology, innovation, irregular but large windfalls",
        "Meena":"spiritual services, arts, charity work, sea-related, medicine",
    }
    sources=SOURCES.get(sign11,"varied income sources")

    d_yogas=[y for y in yogas if any(k in y for k in ("Dhana","Lakshmi","Raj"))]

    # Sudden gains: 8th house
    h8_pl=[p for p,d in pm.items() if d["house"]==8]
    sudden="Strong lottery/inheritance potential — Rahu or Jupiter in 8th" if any(p in h8_pl for p in ("Rahu","Jupiter")) else \
           "Moderate unexpected income possible" if "Moon" in h8_pl else \
           "Earned wealth dominates over windfalls"

    # Debt: 6th lord strength
    l6=hl[6]; l6_ns=ns.get(l6,0)
    debt="Debt risk — 6th lord is strong and active. Maintain disciplined finances." if l6_ns>=1.5 else \
         "Moderate debt indicators — avoid over-leveraging" if l6_ns>=0 else \
         "Low debt risk — 6th lord is weak"

    remedies=_build_remedies(ctx,["Jupiter","Venus",lord_2],"wealth")
    timing=_timing(ctx,[2,11,9],"wealth")

    j_h=jupiter.get("house",1); j_s=jupiter.get("sign",""); j_ns=round(ns.get("Jupiter",0),1)
    parts=[
        f"Jupiter (wealth karaka) in {_ordinal(j_h)}H {j_s}, net strength {j_ns:+.1f} — {'excellent' if j_ns>=2 else 'good' if j_ns>=0 else 'challenged — needs strengthening'}.",
        f"2nd lord {lord_2} (net {round(ns.get(lord_2,0),1):+.1f}) and 11th lord {lord_11} (net {round(ns.get(lord_11,0),1):+.1f}) govern income flow.",
        f"Primary income: {sources}.",
    ]
    if d_yogas: parts.append(f"Wealth yogas: {', '.join(d_yogas)} — significant accumulation potential.")
    parts.append(f"Best financial window: {timing['best_window']}.")

    return {
        "domain":"Wealth & Finance","icon":"₹","score":sc,
        "dhana_yogas":d_yogas,"income_sources":sources,"sudden_gain":sudden,"debt_risk":debt,
        "second_lord":_house_lord_str(ctx,2),"eleventh_lord":_house_lord_str(ctx,11),
        "h2_planets":h2_pl,"h11_planets":h11_pl,
        "dasha_active":result["dasha_active"],
        "timing":timing,"remedies":remedies,"analysis":" ".join(parts),
        "_scoring":result,
    }


# ═══════════════════════════════════════════════════
# DOMAIN 4 — HEALTH
# ═══════════════════════════════════════════════════

def _health(ctx: dict) -> dict:
    pm=ctx["planet_map"]; hl=ctx["house_lords"]; fn=ctx["fn"]; ns=ctx["net_scores"]; yogas=ctx["yogas"]

    # For health, lower score of 6/8/12 = better health
    result_bad=_domain_score(ctx,[6,8,12],karaka="Sun",secondary_houses=[1])
    # Invert: if malefics afflict 6/8/12 domain, health is challenged
    sc=max(15,min(85, 65 - result_bad["raw"]*4))

    sun=pm.get("Sun",{}); moon=pm.get("Moon",{}); mars=pm.get("Mars",{})
    saturn=pm.get("Saturn",{}); lagna=ctx["lagna"]
    lord_1=hl[1]; l1d=pm.get(lord_1,{})

    ORGANS_6H={
        "Mesha":"head, brain, eyes, migraines",
        "Vrishabha":"throat, neck, thyroid, tonsils",
        "Mithuna":"lungs, arms, shoulders, respiratory",
        "Karka":"chest, breasts, stomach, water retention",
        "Simha":"heart, spine, upper back, cardiac",
        "Kanya":"intestines, digestion, liver, skin",
        "Tula":"kidneys, lower back, adrenal, fluid balance",
        "Vrischika":"reproductive, excretory, colon, STDs",
        "Dhanu":"hips, thighs, liver, sciatica",
        "Makara":"knees, bones, joints, teeth, arthritis",
        "Kumbha":"ankles, nervous system, circulation, varicose",
        "Meena":"feet, lymphatic, immune, addictions",
    }
    sign6=ctx["house_signs"][6]
    weak_organs=ORGANS_6H.get(sign6,"general constitution area")

    AYUR={"Mesha":"Pitta","Vrishabha":"Kapha","Mithuna":"Vata","Karka":"Kapha",
          "Simha":"Pitta","Kanya":"Vata","Tula":"Vata","Vrischika":"Pitta",
          "Dhanu":"Pitta","Makara":"Vata","Kumbha":"Vata","Meena":"Kapha"}
    ayur_dosha=AYUR.get(lagna,"Tridoshic")

    moon_h=moon.get("house",1); moon_ns=ns.get("Moon",0)
    mental_ok=moon_h not in (6,8,12) and moon_ns>=-0.5

    mars_h=mars.get("house",0); sat_h=saturn.get("house",0)
    surgery=(mars_h in (6,8) or sat_h==8)
    surgery_txt="Mars/Saturn in 6th or 8th — surgery or accident risk. Time operations carefully." if surgery else \
                "No strong surgery indicators. Preventive healthcare sufficient."

    arishta=[y for y in yogas if any(k in y for k in ("Arishta","Balarishta","Kaal Sarp","Grahan"))]

    remedies=_build_remedies(ctx,["Sun",lord_1,"Moon"],"health")
    timing=_timing(ctx,[1,6,8],"health")

    parts=[
        f"Lagna {lagna} gives {ayur_dosha} Prakriti — balance through appropriate diet and lifestyle.",
        f"6th house in {sign6} indicates vulnerability in: {weak_organs}.",
        f"Lagna lord {lord_1} in {_ordinal(l1d.get('house',1))}H (net {round(ns.get(lord_1,0),1):+.1f}) — {'strong vitality' if ns.get(lord_1,0)>=1 else 'moderate' if ns.get(lord_1,0)>=-1 else 'vitality needs attention'}.",
        f"Mental health: {'✓ Stable Moon indicators' if mental_ok else '⚠ Moon in {}, ns {:.1f} — manage stress proactively'.format(moon_h, moon_ns)}.",
        surgery_txt,
    ]

    return {
        "domain":"Health & Longevity","icon":"✚","score":int(sc),
        "weak_organs":weak_organs,"ayurvedic_dosha":ayur_dosha,
        "mental_health_ok":mental_ok,"surgery_risk":surgery,"surgery_txt":surgery_txt,
        "arishta_doshas":arishta,
        "disease_periods":f"Monitor health during Saturn/Mars dasha over 1st, 6th, 8th houses",
        "first_lord":_house_lord_str(ctx,1),
        "dasha_active":result_bad["dasha_active"],
        "timing":timing,"remedies":remedies,"analysis":" ".join(parts),
        "_scoring":result_bad,
    }


# ═══════════════════════════════════════════════════
# DOMAIN 5 — CHILDREN
# ═══════════════════════════════════════════════════

def _children(ctx: dict) -> dict:
    pm=ctx["planet_map"]; hl=ctx["house_lords"]; fn=ctx["fn"]; ns=ctx["net_scores"]; yogas=ctx["yogas"]

    result=_domain_score(ctx,[5,9],karaka="Jupiter",secondary_houses=[1,11])
    sc=result["score"]

    jupiter=pm.get("Jupiter",{}); sun=pm.get("Sun",{})
    h5_pl=[p for p,d in pm.items() if d["house"]==5]
    lord_5=hl[5]; l5d=pm.get(lord_5,{})

    j_ns=ns.get("Jupiter",0); l5_ns=ns.get(lord_5,0)
    if j_ns>=1 and l5_ns>=0:
        count="2–3 children indicated — Jupiter and 5th lord are strong"
    elif j_ns>=0 and l5_ns>=0:
        count="1–2 children — moderate 5th house strength"
    elif j_ns<-1 and l5_ns<-1:
        count="Challenges in childbearing — Jupiter and 5th lord both weak. Seek Santana Gopala remedy"
    else:
        count="1 child indicated — one of the key planets is weak"

    sign5=ctx["house_signs"][5]
    MALE=["Mesha","Mithuna","Simha","Dhanu","Kumbha"]
    gender="Male child indicated (traditional indicator)" if sign5 in MALE else "Female child indicated (traditional indicator)"

    nature="creative and intelligent" if any(p in h5_pl for p in ("Jupiter","Mercury","Venus")) else \
           "energetic and courageous" if "Mars" in h5_pl else \
           "emotional and artistic" if "Moon" in h5_pl else \
           "disciplined and mature" if "Saturn" in h5_pl else \
           "independent and bright"

    putra_dosh="Putra Dosh" in yogas
    s_yoga=[y for y in yogas if "Santana" in y or "Putra" in y]

    remedies=_build_remedies(ctx,["Jupiter",lord_5],"children")
    timing=_timing(ctx,[5,9],"children")

    return {
        "domain":"Children & Next Generation","icon":"❋","score":sc,
        "count_indicator":count,"gender_indicator":gender,"child_nature":f"Child likely {nature}",
        "putra_dosh":putra_dosh,"santana_yoga":s_yoga,
        "fifth_lord":_house_lord_str(ctx,5),
        "jupiter_position":f"Jupiter in {_ordinal(jupiter.get('house',1))}H {jupiter.get('sign','')} (net {round(j_ns,1):+.1f})",
        "h5_planets":h5_pl,"dasha_active":result["dasha_active"],
        "timing":timing,"remedies":remedies,
        "analysis":f"Jupiter (putra karaka) net {j_ns:+.1f}, 5th lord {lord_5} net {l5_ns:+.1f}. {count}. Child nature: {nature}. {gender}. Best window: {timing['best_window']}.",
        "_scoring":result,
    }


# ═══════════════════════════════════════════════════
# DOMAIN 6 — EDUCATION
# ═══════════════════════════════════════════════════

def _education(ctx: dict) -> dict:
    pm=ctx["planet_map"]; hl=ctx["house_lords"]; fn=ctx["fn"]; ns=ctx["net_scores"]; yogas=ctx["yogas"]

    result=_domain_score(ctx,[4,5],karaka="Mercury",secondary_houses=[9,11])
    sc=result["score"]

    mercury=pm.get("Mercury",{}); jupiter=pm.get("Jupiter",{})
    sign4=ctx["house_signs"][4]; lord_4=hl[4]; lord_5=hl[5]

    STUDY={
        "Mesha":"engineering, sports science, defence, physical therapy, architecture",
        "Vrishabha":"commerce, arts, agriculture, banking, interior design",
        "Mithuna":"journalism, languages, IT, mass communication, mathematics",
        "Karka":"nursing, psychology, hospitality, history, social work",
        "Simha":"medicine, management, drama, literature, leadership, law",
        "Kanya":"medicine, pharmacy, accounting, research, editing, biology",
        "Tula":"law, design, diplomacy, social sciences, fine arts, psychology",
        "Vrischika":"research, forensics, depth psychology, occult, biochemistry",
        "Dhanu":"philosophy, law, education, foreign languages, travel management",
        "Makara":"administration, civil services, engineering, finance, architecture",
        "Kumbha":"computer science, electronics, astrology, innovation, aeronautics",
        "Meena":"spirituality, medicine, arts, marine science, music, photography",
    }
    fields=STUDY.get(sign4,"diverse academic domains")

    v_yogas=[y for y in yogas if any(k in y for k in ("Saraswati","Budhaditya","Raj"))]
    foreign_edu="Rahu" in [p for p,d in pm.items() if d["house"] in (4,5,9)]

    m_ns=round(ns.get("Mercury",0),1)
    j_ns=round(ns.get("Jupiter",0),1)

    remedies=_build_remedies(ctx,["Mercury",lord_4,lord_5],"education")
    timing=_timing(ctx,[4,5,9],"education")

    return {
        "domain":"Education & Skills","icon":"✦","score":sc,
        "study_fields":fields,"vidya_yoga":v_yogas,"foreign_education":foreign_edu,
        "competitive_success":f"{'Strong' if sc>65 else 'Moderate'} competitive exam potential — Mercury net {m_ns:+.1f}",
        "mercury_position":f"Mercury in {_ordinal(mercury.get('house',1))}H (net {m_ns:+.1f})",
        "dasha_active":result["dasha_active"],
        "timing":timing,"remedies":remedies,
        "analysis":f"4th/5th houses govern education. Mercury (intellect) net {m_ns:+.1f}, Jupiter net {j_ns:+.1f}. Best fields: {fields}. {('Vidya yogas: '+', '.join(v_yogas)+'.' if v_yogas else '')} Foreign education: {'indicated' if foreign_edu else 'less prominent'}. Window: {timing['best_window']}.",
        "_scoring":result,
    }


# ═══════════════════════════════════════════════════
# DOMAIN 7 — PROPERTY
# ═══════════════════════════════════════════════════

def _property(ctx: dict) -> dict:
    pm=ctx["planet_map"]; hl=ctx["house_lords"]; fn=ctx["fn"]; ns=ctx["net_scores"]

    result=_domain_score(ctx,[4],karaka="Mars",secondary_houses=[2,11,12])
    sc=result["score"]

    mars=pm.get("Mars",{}); moon=pm.get("Moon",{})
    lord_4=hl[4]; l4d=pm.get(lord_4,{})
    sign4=ctx["house_signs"][4]

    PROP={
        "Mesha":"independent house, open plot, active environment",
        "Vrishabha":"fertile land, luxurious property, garden estate",
        "Mithuna":"apartment in busy locality, multi-story, commercial-adjacent",
        "Karka":"ancestral property, near water body, family home",
        "Simha":"large prestigious property, prominent location, heritage",
        "Kanya":"clean, well-organized, vastu-compliant residential",
        "Tula":"beautifully designed, aesthetically pleasing home",
        "Vrischika":"old or hidden property, remote location, character home",
        "Dhanu":"near temple or hills, open land, spiritual environment",
        "Makara":"durable construction, traditional stone, long-lasting building",
        "Kumbha":"modern society, technology-enabled smart home",
        "Meena":"near water, spiritual or ashram-adjacent, irregular shape",
    }
    prop_type=PROP.get(sign4,"varied property type")

    mars_ns=ns.get("Mars",0); l4_ns=ns.get(lord_4,0)
    multi_prop=mars_ns>=1.5 or (mars.get("house") in (4,2,11) and mars_ns>=0)
    domestic_ok=moon.get("house")==4 or ns.get("Moon",0)>=0.5

    remedies=_build_remedies(ctx,["Mars",lord_4],"property")
    timing=_timing(ctx,[4,2,12],"property")

    return {
        "domain":"Property & Home","icon":"⌂","score":sc,
        "property_type":prop_type,"multiple_properties":multi_prop,"domestic_happiness":domestic_ok,
        "vastu":f"4th house in {'earthy sign — Vastu compliance very important' if sign4 in ('Vrishabha','Kanya','Makara') else 'current sign — standard Vastu principles apply'}",
        "fourth_lord":_house_lord_str(ctx,4),
        "mars_position":f"Mars in {_ordinal(mars.get('house',1))}H (net {round(mars_ns,1):+.1f})",
        "dasha_active":result["dasha_active"],
        "timing":timing,"remedies":remedies,
        "analysis":f"4th lord {lord_4} net {round(l4_ns,1):+.1f}. Mars (property karaka) net {round(mars_ns,1):+.1f}. Property type: {prop_type}. {'Multiple properties possible.' if multi_prop else ''} Best purchase window: {timing['best_window']}.",
        "_scoring":result,
    }


# ═══════════════════════════════════════════════════
# DOMAIN 8 — CHALLENGES & DOSHAS
# ═══════════════════════════════════════════════════

def _challenges(ctx: dict) -> dict:
    pm=ctx["planet_map"]; hl=ctx["house_lords"]; fn=ctx["fn"]; ns=ctx["net_scores"]; yogas=ctx["yogas"]
    rahu=pm.get("Rahu",{}); ketu=pm.get("Ketu",{}); mars=pm.get("Mars",{}); saturn=pm.get("Saturn",{})

    doshas_found=[]
    if "Kaal Sarp Dosh" in yogas:
        doshas_found.append({"name":"Kaal Sarp Dosh","severity":"High",
            "desc":"All planets hemmed between Rahu and Ketu. Intense karmic patterns — obstacles followed by sudden dramatic rises. Can produce exceptional achievers when worked with consciously."})
    if "Mangal Dosh" in yogas:
        mars_h=mars.get("house",0)
        doshas_found.append({"name":"Mangal Dosh","severity":"Moderate",
            "desc":f"Mars in {_ordinal(mars_h)} house — energy imbalance affecting relationships and partnerships. Match with partner of similar pattern or apply Mangal remedies before marriage."})
    if "Pitru Dosh" in yogas:
        doshas_found.append({"name":"Pitru Dosh","severity":"Moderate",
            "desc":"Ancestral karmic debt indicated. Offer tarpan to ancestors on Amavasya and during Pitru Paksha. Perform Shraddha rituals annually."})
    for y in yogas:
        if "Grahan Dosh" in y:
            doshas_found.append({"name":y,"severity":"Moderate",
                "desc":"Rahu or Ketu eclipsing a luminary (Sun/Moon) — challenges to identity (Sun) or emotional stability (Moon). Remedies: Chant Aditya Hridayam or Chandra mantra."})

    # Check Sade Sati
    moon_sign_idx=RASHI.index(pm.get("Moon",{}).get("sign","Mesha")) if pm.get("Moon",{}).get("sign") in RASHI else 0
    sat_sign_idx=RASHI.index(saturn.get("sign","Mesha")) if saturn.get("sign") in RASHI else 0
    sade_sati=abs(sat_sign_idx-moon_sign_idx) in (0,1,11)
    if sade_sati:
        doshas_found.append({"name":"Shani Sade Sati","severity":"Moderate",
            "desc":"Saturn within 1 sign of natal Moon — 7.5-year karmic cleansing. Tests come to purify and strengthen. Discipline and patience are essential during this period."})

    sc=max(15, min(85, 80-len(doshas_found)*12))

    h6_malefics=[p for p in ("Saturn","Mars","Rahu") if pm.get(p,{}).get("house")==6]
    legal_risk=len(h6_malefics)>0

    remedies=_build_remedies(ctx,
        (["Rahu","Ketu"] if "Kaal Sarp Dosh" in yogas else [])+(["Mars"] if "Mangal Dosh" in yogas else [])+
        (["Saturn"] if sade_sati else [])+(["Sun"] if "Pitru Dosh" in yogas else []),
        "challenges")

    def narrate():
        if not doshas_found:
            return "No major doshas detected in this chart. The planetary configuration is relatively free from serious afflictions. Minor challenges exist in all charts but none reach the threshold of a classical dosha."
        names=", ".join(d["name"] for d in doshas_found)
        return f"{len(doshas_found)} dosha(s) detected: {names}. Each can be significantly mitigated through appropriate remedies, timing of important decisions, and conscious karmic work. Doshas are not permanent curses but karmic patterns to be understood and transcended."

    return {
        "domain":"Challenges & Doshas","icon":"⚡","score":sc,
        "kaal_sarp":"Kaal Sarp Dosh" in yogas,"mangal_dosh":"Mangal Dosh" in yogas,
        "sade_sati":sade_sati,"pitru_dosh":"Pitru Dosh" in yogas,
        "grahan_dosh":any("Grahan" in y for y in yogas),
        "doshas_found":doshas_found,"dosha_count":len(doshas_found),
        "legal_risk":legal_risk,
        "legal_txt":f"6th house afflicted by {', '.join(h6_malefics)} — litigation and conflict with authority possible." if legal_risk else "No strong legal trouble indicators.",
        "remedies":remedies,"dasha_active":False,
        "timing":{"best_window":"N/A — apply remedies continuously","confidence":"—","challenge":"—","dasha_quality":0,"transit_score":0},
        "analysis":narrate(),
    }


# ═══════════════════════════════════════════════════
# DOMAIN 9 — TRAVEL & FOREIGN
# ═══════════════════════════════════════════════════

def _travel(ctx: dict) -> dict:
    pm=ctx["planet_map"]; hl=ctx["house_lords"]; fn=ctx["fn"]; ns=ctx["net_scores"]

    result=_domain_score(ctx,[12,9],karaka="Rahu",secondary_houses=[3,7])
    sc=result["score"]

    rahu=pm.get("Rahu",{}); moon=pm.get("Moon",{})
    lord_12=hl[12]; lord_9=hl[9]
    h12_pl=[p for p,d in pm.items() if d["house"]==12]
    h9_pl=[p for p,d in pm.items() if d["house"]==9]

    rahu_h=rahu.get("house",0)
    foreign=rahu_h in (1,7,9,12) or "Rahu" in h12_pl or (ns.get("Rahu",0)>=0 and rahu_h in (4,5))

    l9=hl[9]; l9_ns=ns.get(l9,0)
    visa_ok=l9_ns>=0.5 or "Jupiter" in h9_pl

    sign4=ctx["house_signs"][4]
    DIR={"Mesha":"East","Vrishabha":"South","Mithuna":"North","Karka":"North-West",
         "Simha":"East","Kanya":"South-East","Tula":"West","Vrischika":"North",
         "Dhanu":"North-East","Makara":"South","Kumbha":"West","Meena":"North-East"}
    direction=DIR.get(sign4,"Variable")

    remedies=_build_remedies(ctx,["Rahu",lord_12],"travel")
    timing=_timing(ctx,[12,9,3],"travel")

    r_ns=round(ns.get("Rahu",0),1); l12_ns=round(ns.get(lord_12,0),1)

    return {
        "domain":"Travel & Foreign","icon":"✈","score":sc,
        "foreign_settlement":foreign,"visa_success":visa_ok,"direction":direction,
        "overseas_career":f"Overseas career {'strongly indicated — Rahu in 10th' if rahu_h==10 else 'possible via Rahu Dasha' if rahu_h in (1,9,12) else 'less prominent in this chart'}",
        "twelfth_lord":_house_lord_str(ctx,12),
        "rahu_position":f"Rahu in {_ordinal(rahu_h)}H (net {r_ns:+.1f})",
        "dasha_active":result["dasha_active"],
        "timing":timing,"remedies":remedies,
        "analysis":f"12th lord {lord_12} (net {l12_ns:+.1f}). Rahu in {_ordinal(rahu_h)}H (net {r_ns:+.1f}). Foreign settlement: {'strongly indicated' if foreign else 'less prominent — Rahu needs stronger 12th house activation'}. Direction: {direction}. Window: {timing['best_window']}.",
        "_scoring":result,
    }


# ═══════════════════════════════════════════════════
# DOMAIN 10 — SPIRITUALITY
# ═══════════════════════════════════════════════════

def _spirituality(ctx: dict) -> dict:
    pm=ctx["planet_map"]; hl=ctx["house_lords"]; fn=ctx["fn"]; ns=ctx["net_scores"]; yogas=ctx["yogas"]

    result=_domain_score(ctx,[9,12],karaka="Jupiter",secondary_houses=[1,5,8])
    sc=result["score"]

    ketu=pm.get("Ketu",{}); jupiter=pm.get("Jupiter",{})
    lord_9=hl[9]; lord_12=hl[12]

    ketu_h=ketu.get("house",1)
    spiritual_inc=(ketu_h in (1,5,9,12) and ns.get("Ketu",0)>=-1) or (ns.get("Jupiter",0)>=1 and jupiter.get("house") in (9,12))

    moksha=[y for y in yogas if any(k in y for k in ("Vipreet","Moksha","Kaal Sarp"))]

    moon_nak=pm.get("Moon",{}).get("nakshatra","Ashwini")
    DEITY={
        "Ashwini":"Ashwini Kumaras","Bharani":"Lord Yama","Krittika":"Lord Agni",
        "Rohini":"Lord Brahma / Krishna","Mrigashira":"Soma (Chandra)","Ardra":"Lord Shiva / Rudra",
        "Punarvasu":"Mother Aditi","Pushya":"Lord Brihaspati / Shiva","Ashlesha":"Naga Devatas",
        "Magha":"Pitrus (Ancestors)","Purva Phalguni":"Lord Bhaga","Uttara Phalguni":"Lord Aryaman",
        "Hasta":"Surya (Savitri)","Chitra":"Lord Vishwakarma","Swati":"Lord Vayu",
        "Vishakha":"Indra and Agni","Anuradha":"Lord Mitra","Jyeshtha":"Lord Indra",
        "Mula":"Nirrti (Kali)","Purva Ashadha":"Apas (Water deities)","Uttara Ashadha":"Vishwadevas",
        "Shravana":"Lord Vishnu","Dhanishta":"Ashta Vasus","Shatabhisha":"Lord Varuna",
        "Purva Bhadrapada":"Aja Ekapada","Uttara Bhadrapada":"Ahir Budhanya","Revati":"Pusha",
    }
    deity=DEITY.get(moon_nak,"Lord Vishnu")

    ketu_domain=["self-mastery","wealth and family","communication","home and comfort",
                 "creativity and past merit","service and karma","partnerships","occult and transformation",
                 "dharma and teacher","career and action","social connections","liberation and loss"][ketu_h-1]
    past_karma=f"Ketu in {_ordinal(ketu_h)} house — past-life mastery in {ketu_domain}. This life, the soul seeks to balance through the opposite {_ordinal(((ketu_h+5)%12)+1)} house themes."

    sign9=ctx["house_signs"][9]
    DHARMA={"Mesha":"courage and individual initiative","Vrishabha":"sensory service and material dharma",
            "Mithuna":"communication and mental dharma","Karka":"emotional service and family dharma",
            "Simha":"leadership and creative dharma","Kanya":"service, healing and perfection",
            "Tula":"justice, balance and relational dharma","Vrischika":"transformation and occult dharma",
            "Dhanu":"knowledge, teaching and philosophical dharma","Makara":"discipline and structural dharma",
            "Kumbha":"innovation, community and humanitarian dharma","Meena":"surrender, compassion and spiritual dharma"}
    dharma=DHARMA.get(sign9,"alignment with cosmic order")

    remedies=_build_remedies(ctx,["Jupiter","Ketu"],"spirituality")
    timing=_timing(ctx,[9,12,5],"spirituality")

    j_ns=round(ns.get("Jupiter",0),1); l9_ns=round(ns.get(lord_9,0),1)

    return {
        "domain":"Spirituality & Karma","icon":"☯","score":sc,
        "spiritual_inclination":spiritual_inc,"moksha_yoga":moksha,"deity":deity,"past_karma":past_karma,
        "dharma_path":f"9th house in {sign9} — dharma through {dharma}",
        "ninth_lord":_house_lord_str(ctx,9),
        "ketu_position":f"Ketu in {_ordinal(ketu_h)}H",
        "dasha_active":result["dasha_active"],
        "timing":timing,"remedies":remedies,
        "analysis":f"9th lord {lord_9} net {l9_ns:+.1f}. Jupiter net {j_ns:+.1f}. {'Strong spiritual inclination — Ketu in spiritual house.' if spiritual_inc else 'Spiritual growth through material experience first.'} {past_karma} Deity: {deity}. Dharma: {dharma}.",
        "_scoring":result,
    }


# ═══════════════════════════════════════════════════
# MASTER FUNCTION
# ═══════════════════════════════════════════════════

def analyse_all_domains(chart: dict) -> dict:
    ctx = _build_ctx(chart)
    return {
        "lagna":      ctx["lagna"],
        "mahadasha":  ctx["mahadasha"],
        "antardasha": ctx["antardasha"],
        "yogas_detected": ctx["yogas"],
        "domains": {
            "marriage":    _marriage(ctx),
            "career":      _career(ctx),
            "wealth":      _wealth(ctx),
            "health":      _health(ctx),
            "children":    _children(ctx),
            "education":   _education(ctx),
            "property":    _property(ctx),
            "challenges":  _challenges(ctx),
            "travel":      _travel(ctx),
            "spirituality":_spirituality(ctx),
        }
    }
