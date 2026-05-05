"""
festival_engine.py — Tithi-based Hindu Festival Engine + Dynamic Horoscope Engine
All festivals computed from live Swiss Ephemeris positions. Zero hardcoded Gregorian dates.
Horoscope text generated from real planet transits, house positions, strengths.
"""
'''
import swisseph as swe
from datetime import datetime, timedelta, timezone
from math import floor

swe.set_ephe_path('.')
swe.set_sid_mode(swe.SIDM_LAHIRI)

IST_OFFSET = 5.5
NAK_DIV    = 360 / 27  # 13.333...°

# ═══════════════════════════════════════════════════════════════
# REFERENCE DATA
# ═══════════════════════════════════════════════════════════════

TITHI_NAMES = [
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami",
    "Shashthi","Saptami","Ashtami","Navami","Dashami",
    "Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Purnima",
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami",
    "Shashthi","Saptami","Ashtami","Navami","Dashami",
    "Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Amavasya",
]

NAKSHATRA_NAMES = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
    "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha",
    "Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha",
    "Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
    "Uttara Bhadrapada","Revati",
]

RASHI_NAMES = [
    "Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya",
    "Tula","Vrischika","Dhanu","Makara","Kumbha","Meena",
]

RASHI_EN = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces",
]

YOGA_NAMES = [
    "Vishkumbha","Preeti","Ayushman","Saubhagya","Shobhana",
    "Atiganda","Sukarma","Dhriti","Shoola","Ganda","Vriddhi",
    "Dhruva","Vyaghata","Harshana","Vajra","Siddhi","Vyatipata",
    "Variyana","Parigha","Shiva","Siddha","Sadhya","Shubha",
    "Shukla","Brahma","Indra","Vaidhriti",
]

KARANA_NAMES = ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"]

# ═══════════════════════════════════════════════════════════════
# FESTIVAL RULES — 100% tithi / nakshatra / solar-ingress based
# paksha : "Shukla" | "Krishna" | "any"
# tithi  : 1-15 within the paksha (1=Pratipada … 15=Purnima/Amavasya)
# month  : solar rashi index 1-12 (Mesha=1…Meena=12) or None=any
# nakshatra : required Moon nakshatra or None
# sun_ingress: True = festival fires on first day Sun enters `month` sign
# ═══════════════════════════════════════════════════════════════
FESTIVAL_RULES = [
    # ── Shukla Paksha ────────────────────────────────────────────
    dict(paksha="Shukla",  tithi=1,  month=None, name="Shukla Pratipada",
         icon="🌒", desc="First day of waxing moon — auspicious for new beginnings",
         tag="vrat", remedies="Start new ventures, offer flowers to Devi"),

    dict(paksha="Shukla",  tithi=4,  month=4,  name="Ganesh Chaturthi",
         icon="🐘", desc="Birth of Lord Ganesha — worship with modak and 21 durva blades",
         tag="major", remedies="Fast, offer modak, chant Ganpati Atharvashirsha 108×"),

    dict(paksha="Shukla",  tithi=4,  month=None, name="Vinayak Chaturthi",
         icon="🐘", desc="Monthly Ganesha worship — remove obstacles in all endeavours",
         tag="vrat", remedies="Offer modak and durva, chant Om Gam Ganapataye Namah"),

    dict(paksha="Shukla",  tithi=5,  month=10, name="Vasant Panchami",
         icon="🌼", desc="Saraswati Puja — goddess of learning, arts and wisdom worshipped in yellow",
         tag="major", remedies="Wear yellow, offer yellow flowers to Saraswati, begin new studies"),

    dict(paksha="Shukla",  tithi=6,  month=None, name="Skanda Sashti",
         icon="⚔️", desc="Worship of Lord Kartikeya (Murugan) — victory over inner demons",
         tag="festival", remedies="Fast, recite Kandha Sashti Kavacham, offer red flowers"),

    dict(paksha="Shukla",  tithi=7,  month=None, name="Sapta Tithi",
         icon="☀️", desc="Seventh lunar day — auspicious for Sun worship",
         tag="vrat", remedies="Offer water to Sun, recite Aditya Hridayam"),

    dict(paksha="Shukla",  tithi=8,  month=None, name="Durgashtami",
         icon="🔱", desc="Monthly Durga worship — invoke strength and protection",
         tag="vrat", remedies="Offer kumkum and red flowers to Durga, fast half-day"),

    dict(paksha="Shukla",  tithi=9,  month=None, name="Ram Navami",
         icon="🏹", desc="Birthday of Lord Rama — recite Ramcharitmanas, fast till evening",
         tag="major", remedies="Fast, recite Ramayana, offer tulsi and flowers to Ram"),

    dict(paksha="Shukla",  tithi=11, month=None, name="Ekadashi",
         icon="🌿", desc="Sacred fasting day of Lord Vishnu — most powerful day for moksha",
         tag="ekadashi", remedies="Fast on Ekadashi, chant Vishnu Sahasranama, stay awake at night"),

    dict(paksha="Shukla",  tithi=12, month=None, name="Dwadashi (Vaishnava)",
         icon="🪷", desc="Ekadashi parana day — break fast with tulsi water at auspicious time",
         tag="vrat", remedies="Break Ekadashi fast correctly, offer tulsi to Vishnu"),

    dict(paksha="Shukla",  tithi=13, month=None, name="Pradosh Vrat",
         icon="🕉️", desc="Auspicious evening vrat for Lord Shiva — performed at dusk",
         tag="vrat", remedies="Visit Shiva temple at dusk, offer bilva leaves, fast till evening"),

    dict(paksha="Shukla",  tithi=14, month=9,  name="Maha Shivaratri",
         icon="🕉️", desc="Great night of Lord Shiva — most sacred night of the entire year",
         tag="major", remedies="All-night vigil, fast, bathe Shivalinga with milk, bilva, honey"),

    dict(paksha="Shukla",  tithi=14, month=None, name="Shiva Chaturdashi",
         icon="🕉️", desc="Monthly Masik Shivaratri — worship Shiva at midnight",
         tag="vrat", remedies="Fast, offer bilva, light lamps for Shiva at midnight"),

    dict(paksha="Shukla",  tithi=15, month=None, name="Purnima",
         icon="🌕", desc="Full Moon — sacred for ancestor rites, charity and sattvic practices",
         tag="purnima", remedies="Donate, bathe in sacred river, observe fast, light lamps"),

    dict(paksha="Shukla",  tithi=15, month=1,  name="Holi Purnima (Holika Dahan)",
         icon="🎨", desc="Holika Dahan — sacred bonfire symbolising victory of devotion over evil",
         tag="major", remedies="Perform Holika puja, walk around fire 3×, pray for protection"),

    dict(paksha="Shukla",  tithi=15, month=2,  name="Buddha Purnima",
         icon="☸️", desc="Birth of Gautama Buddha — practice ahimsa, compassion and dana",
         tag="festival", remedies="Observe silence, donate food, practise loving-kindness meditation"),

    dict(paksha="Shukla",  tithi=15, month=3,  name="Guru Purnima",
         icon="🪷", desc="Honour your Guru — offer gratitude to teachers and spiritual lineage",
         tag="major", remedies="Serve your guru, study scriptures, donate to teachers"),

    dict(paksha="Shukla",  tithi=15, month=5,  name="Sharad Purnima",
         icon="🌕", desc="Moon at its fullest — prepare kheer, offer to moonlight overnight",
         tag="major", remedies="Prepare rice kheer, place under moonlight, consume at sunrise"),

    dict(paksha="Shukla",  tithi=15, month=6,  name="Kartik Purnima (Dev Deepawali)",
         icon="🪔", desc="Dev Deepawali — gods descend to bathe in Ganga, light lamps on river",
         tag="major", remedies="Light 108 diyas on river bank, take Kartik bath at sunrise"),

    dict(paksha="Shukla",  tithi=15, month=7,  name="Raksha Bandhan",
         icon="🧵", desc="Sacred sibling bond — sister ties rakhi for brother's protection",
         tag="major", remedies="Perform rakhi ceremony during auspicious muhurat, pray for sibling"),

    # ── Krishna Paksha ───────────────────────────────────────────
    dict(paksha="Krishna", tithi=4,  month=None, name="Sankashta Chaturthi",
         icon="🐘", desc="Monthly Ganesha vrat on Krishna Chaturthi — remove accumulated obstacles",
         tag="vrat", remedies="Fast until moon rise, offer modak, chant Sankat Nashan Ganesh Stotra"),

    dict(paksha="Krishna", tithi=8,  month=4,  name="Janmashtami",
         icon="🦚", desc="Birthday of Lord Krishna — midnight celebration, dahi-handi, bhajans",
         tag="major", remedies="Fast until midnight, perform Krishna puja, sing bhajans all night"),

    dict(paksha="Krishna", tithi=8,  month=None, name="Masik Ashtami (Kalashtami)",
         icon="🔱", desc="Monthly Bhairav worship — Kaal Bhairav is worshipped at night",
         tag="vrat", remedies="Fast, visit Bhairav temple at night, offer sesame oil lamps"),

    dict(paksha="Krishna", tithi=11, month=None, name="Ekadashi",
         icon="🌿", desc="Sacred fasting day of Lord Vishnu — equally powerful as Shukla Ekadashi",
         tag="ekadashi", remedies="Fast, chant Vishnu Sahasranama, sleep on floor, avoid rice"),

    dict(paksha="Krishna", tithi=13, month=None, name="Pradosh Vrat",
         icon="🕉️", desc="Evening Shiva worship — Shiva and Parvati are happy at this time",
         tag="vrat", remedies="Shiva puja at dusk, offer bilva and white flowers, fast till evening"),

    dict(paksha="Krishna", tithi=13, month=5,  name="Dhanteras",
         icon="💰", desc="Worship of Dhanvantari and Yama — buy metals for prosperity",
         tag="major", remedies="Light 13 diyas facing south, worship Lakshmi and Dhanvantari"),

    dict(paksha="Krishna", tithi=14, month=5,  name="Naraka Chaturdashi (Choti Diwali)",
         icon="🪔", desc="Victory over demon Narakasura — bathe before sunrise for liberation",
         tag="major", remedies="Bathe before sunrise with sesame oil, light lamps, pray to Yama"),

    dict(paksha="Krishna", tithi=14, month=None, name="Shiva Chaturdashi (Masik Shivaratri)",
         icon="🕉️", desc="Monthly Shiva worship night — Shiva is at his most accessible",
         tag="vrat", remedies="Fast, offer milk to Shivalinga at midnight, chant Om Namah Shivaya"),

    dict(paksha="Krishna", tithi=15, month=None, name="Amavasya",
         icon="🌑", desc="New Moon — most sacred day for Pitru tarpan and ancestor worship",
         tag="amavasya", remedies="Offer water tarpan to ancestors, donate in their name, light sesame lamps"),

    dict(paksha="Krishna", tithi=15, month=5,  name="Diwali (Lakshmi Puja)",
         icon="🪔", desc="Festival of lights — Goddess Lakshmi worshipped for wealth and prosperity",
         tag="major", remedies="Light clay diyas, perform Lakshmi-Ganesh puja at night, donate to poor"),

    dict(paksha="Krishna", tithi=15, month=6,  name="Kartik Amavasya",
         icon="🌑", desc="Sacred new moon in Kartik — light lamps on rivers for ancestors",
         tag="major", remedies="Light diyas on flowing water, offer tarpan to departed ancestors"),

    dict(paksha="Krishna", tithi=15, month=8,  name="Mahalaya Amavasya (Pitru Paksha End)",
         icon="🌑", desc="Final day of Pitru Paksha — most powerful day for ancestor worship",
         tag="major", remedies="Perform Shraddha and tarpan, donate food in ancestor's name"),

    # ── Nakshatra-based ──────────────────────────────────────────
    dict(paksha="any", tithi=None, month=None, nakshatra="Pushya",
         name="Pushya Nakshatra", icon="⭐",
         desc="Most auspicious nakshatra — ideal for beginning new work, buying gold, studies",
         tag="nakshatra", remedies="Begin important work, buy gold or property, visit temple"),

    dict(paksha="any", tithi=None, month=None, nakshatra="Rohini",
         name="Rohini Nakshatra", icon="🌸",
         desc="Moon's favourite nakshatra — excellent for agriculture, arts and relationships",
         tag="nakshatra", remedies="Plant seeds, begin creative projects, worship Moon"),

    dict(paksha="any", tithi=None, month=None, nakshatra="Hasta",
         name="Hasta Nakshatra", icon="✋",
         desc="Nakshatra of craftsmanship — ideal for trade, artisans and healing work",
         tag="nakshatra", remedies="Engage in skilled work, visit Surya temple"),

    # ── Solar Ingress (Sankranti) ────────────────────────────────
    dict(paksha="any", tithi=None, month=1,  sun_ingress=True,
         name="Mesha Sankranti (Vedic New Year)", icon="🌅",
         desc="Sun enters Aries — Vedic Solar New Year, most important Sankranti",
         tag="major", remedies="Bathe at sunrise, donate sesame, worship Surya facing East"),

    dict(paksha="any", tithi=None, month=10, sun_ingress=True,
         name="Makar Sankranti", icon="🪁",
         desc="Sun enters Capricorn — Uttarayan begins, harvest festival across India",
         tag="major", remedies="Take holy dip before sunrise, donate til-gur, fly kites"),

    dict(paksha="any", tithi=None, month=4,  sun_ingress=True,
         name="Karka Sankranti (Dakshinayan)", icon="☀️",
         desc="Sun enters Cancer — Dakshinayan begins, ancestors descend",
         tag="sankranti", remedies="Donate, observe fast, perform pitru tarpan"),

    dict(paksha="any", tithi=None, month=2,  sun_ingress=True,
         name="Vrishabha Sankranti", icon="☀️",
         desc="Sun enters Taurus — auspicious for land, agriculture and wealth",
         tag="sankranti", remedies="Donate cow's ghee, worship Lakshmi"),

    dict(paksha="any", tithi=None, month=None, sun_ingress=True,
         name="Masa Sankranti", icon="☀️",
         desc="Monthly solar ingress — Sun changes sign, auspicious for charity",
         tag="sankranti", remedies="Donate, bathe, pray to Surya Narayan"),
]

# ═══════════════════════════════════════════════════════════════
# EPHEMERIS HELPERS
# ═══════════════════════════════════════════════════════════════

def _jd_now():
    now = datetime.now(timezone.utc)
    return swe.julday(now.year, now.month, now.day,
                      now.hour + now.minute/60 + now.second/3600)

def _panchang_at(jd):
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun  = swe.calc_ut(jd, swe.SUN,  FLAGS)[0][0]
    moon = swe.calc_ut(jd, swe.MOON, FLAGS)[0][0]
    diff = (moon - sun) % 360
    tithi_idx = int(diff / 12)  # 0-29
    paksha    = "Shukla" if tithi_idx < 15 else "Krishna"
    tithi_no  = (tithi_idx % 15) + 1   # 1-15 in each paksha
    nak_idx   = int(moon / NAK_DIV) % 27
    sun_sign  = int(sun / 30) + 1      # 1-12
    return {
        "tithi_idx":  tithi_idx,
        "tithi_no":   tithi_no,
        "paksha":     paksha,
        "nak_name":   NAKSHATRA_NAMES[nak_idx],
        "sun_sign":   sun_sign,
        "sun":        sun,
        "moon":       moon,
        "diff":       diff,
    }

def _jd_to_date(jd):
    y, m, d, _ = swe.revjul(jd)
    return datetime(int(y), int(m), int(d))

def _match_rule(rule, pan, prev_sun_sign):
    """Returns True when festival rule matches today's panchang."""
    # --- tithi check ---
    if rule.get("tithi") is not None:
        if pan["tithi_no"] != rule["tithi"]:
            return False
        rp = rule.get("paksha", "any")
        if rp != "any" and pan["paksha"] != rp:
            return False

    # --- nakshatra check ---
    if rule.get("nakshatra"):
        if pan["nak_name"] != rule["nakshatra"]:
            return False

    # --- solar month / ingress check ---
    if rule.get("sun_ingress"):
        if rule.get("month"):
            # fires on first day sun is in that sign (ingress day)
            if pan["sun_sign"] != rule["month"] or prev_sun_sign == rule["month"]:
                return False
        else:
            # any ingress
            if pan["sun_sign"] == prev_sun_sign:
                return False
    elif rule.get("month") is not None:
        if pan["sun_sign"] != rule["month"]:
            return False

    return True

# ═══════════════════════════════════════════════════════════════
# PUBLIC — FESTIVAL API
# ═══════════════════════════════════════════════════════════════

def get_festivals_range(days: int = 60) -> list:
    results = []
    seen    = set()
    jd_start = _jd_now()
    prev_sun_sign = _panchang_at(jd_start - 1)["sun_sign"]

    for i in range(days):
        jd  = jd_start + i
        pan = _panchang_at(jd)
        dt  = _jd_to_date(jd)
        date_str = dt.strftime("%Y-%m-%d")
        is_today = (i == 0)

        for rule in FESTIVAL_RULES:
            if _match_rule(rule, pan, prev_sun_sign):
                key = (date_str, rule["name"])
                if key not in seen:
                    seen.add(key)
                    results.append({
                        "date":      date_str,
                        "display":   "Today" if is_today else dt.strftime("%d %b"),
                        "name":      rule["name"],
                        "icon":      rule["icon"],
                        "desc":      rule["desc"],
                        "tag":       rule["tag"],
                        "remedies":  rule.get("remedies", ""),
                        "paksha":    pan["paksha"],
                        "tithi":     TITHI_NAMES[pan["tithi_idx"]],
                        "nakshatra": pan["nak_name"],
                        "is_today":  is_today,
                    })
        prev_sun_sign = pan["sun_sign"]

    results.sort(key=lambda x: x["date"])
    return results


def get_today_festivals() -> list:
    return [f for f in get_festivals_range(1) if f["is_today"]]


def get_upcoming_festivals(limit: int = 12) -> list:
    return get_festivals_range(90)[:limit]


# ═══════════════════════════════════════════════════════════════
# DYNAMIC HOROSCOPE ENGINE
# Fully derived from live planetary transits — no static text
# ═══════════════════════════════════════════════════════════════

PLANET_IDS = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus":   swe.VENUS,
    "Mars":    swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn":  swe.SATURN,
    "Rahu":    swe.TRUE_NODE,
}

# Exaltation / debilitation / own sign — 1-based sign numbers
EXALTATION   = dict(Sun=1,  Moon=2,  Mars=10, Mercury=6,  Jupiter=4,  Venus=12, Saturn=7)
DEBILITATION = dict(Sun=7,  Moon=8,  Mars=4,  Mercury=12, Jupiter=10, Venus=6,  Saturn=1)
OWN_SIGNS    = dict(Sun=[5],Moon=[4],Mars=[1,8],Mercury=[3,6],Jupiter=[9,12],Venus=[2,7],Saturn=[10,11])

# Natural benefic/malefic
PLANET_NATURE = {
    "Jupiter": +2, "Venus": +2, "Moon": +1, "Mercury": +1,
    "Sun":  0, "Mars": -1, "Saturn": -2, "Rahu": -1, "Ketu": -1,
}

PLANET_KEYWORDS = {
    "Sun":     "authority, vitality, recognition, father, government",
    "Moon":    "emotions, intuition, mother, public, nourishment",
    "Mercury": "intellect, communication, business, logic, skin",
    "Venus":   "love, beauty, arts, marriage, luxury",
    "Mars":    "courage, energy, siblings, conflict, land",
    "Jupiter": "wisdom, expansion, children, wealth, spirituality",
    "Saturn":  "karma, discipline, delay, service, longevity",
    "Rahu":    "obsession, foreign, technology, illusion, ambition",
    "Ketu":    "detachment, spirituality, past karma, liberation",
}

HOUSE_DOMAIN = {
    1:"self and personality",   2:"wealth and family",
    3:"courage and communication", 4:"home and mother",
    5:"children and intelligence", 6:"health and enemies",
    7:"marriage and partnerships", 8:"transformation and longevity",
    9:"luck and dharma",          10:"career and status",
    11:"gains and fulfilment",    12:"spirituality and losses",
}

NAKSHATRA_QUALITY = {
    "Ashwini":1,"Bharani":-1,"Krittika":0,"Rohini":2,"Mrigashira":1,
    "Ardra":-1,"Punarvasu":2,"Pushya":3,"Ashlesha":-1,"Magha":-1,
    "Purva Phalguni":-1,"Uttara Phalguni":2,"Hasta":2,"Chitra":1,
    "Swati":1,"Vishakha":-1,"Anuradha":2,"Jyeshtha":-1,"Mula":-1,
    "Purva Ashadha":-1,"Uttara Ashadha":2,"Shravana":2,"Dhanishta":1,
    "Shatabhisha":-1,"Purva Bhadrapada":-1,"Uttara Bhadrapada":2,"Revati":2,
}

TITHI_QUALITY = {
    0:+2, 1:+2, 2:+2, 4:+1, 5:+1, 10:+2, 11:+1, 14:+2,  # Pratipada,Dwi,Tri,Panch,Shash,Ekad,Dwad,Purnima
    3:-1, 7:-1, 8:-1, 12:-1, 13:-1, 29:-2,                # Chauth,Asht,Navam,Trayd,Chaturd,Amavasya
}

HOUSE_TIP = {
    1:"Focus on personal presentation and first impressions. Start something new for yourself.",
    2:"Review finances and savings. Reconnect with family over a meal.",
    3:"Excellent for writing, speaking, calls and short journeys. Sign documents.",
    4:"Spend time at home. Property and mother-related matters are highlighted.",
    5:"Creative projects, speculative investments and children are in focus.",
    6:"Address health issues promptly. Settle outstanding debts or conflicts early.",
    7:"Partnership and marriage matters deserve attention. Compromise openly.",
    8:"Avoid risky investments. Day favours inner transformation and occult study.",
    9:"Seek guidance from elders or teachers. Long-distance travel is auspicious.",
    10:"Career decisions bring recognition. Connect with senior colleagues.",
    11:"Networking and unexpected income. Meet friends and pursue social goals.",
    12:"Meditate and retreat inward. Foreign connections or hospital visits possible.",
}

NAK_MANTRAS = {
    "Ashwini":"Om Ashwinau Tejase Namah","Bharani":"Om Yama Dharmarajaya Namah",
    "Krittika":"Om Agni Devaya Namah","Rohini":"Om Brahma Devaya Namah",
    "Mrigashira":"Om Soma Devaya Namah","Ardra":"Om Rudraya Namah",
    "Punarvasu":"Om Adityaya Namah","Pushya":"Om Brihaspataye Namah",
    "Ashlesha":"Om Sarpebhyo Namah","Magha":"Om Pitribhyo Namah",
    "Purva Phalguni":"Om Bhagaya Namah","Uttara Phalguni":"Om Arya Devaya Namah",
    "Hasta":"Om Savitri Devaya Namah","Chitra":"Om Vishwakarma Devaya Namah",
    "Swati":"Om Vayu Devaya Namah","Vishakha":"Om Indra Agnibhyam Namah",
    "Anuradha":"Om Mitra Devaya Namah","Jyeshtha":"Om Indra Devaya Namah",
    "Mula":"Om Nirriti Devaya Namah","Purva Ashadha":"Om Jala Devaya Namah",
    "Uttara Ashadha":"Om Vishwe Devebhyo Namah","Shravana":"Om Vishnu Devaya Namah",
    "Dhanishta":"Om Ashta Vasebhyo Namah","Shatabhisha":"Om Varuna Devaya Namah",
    "Purva Bhadrapada":"Om Aja Ekapadaya Namah",
    "Uttara Bhadrapada":"Om Ahir Budhanyaya Namah","Revati":"Om Pusha Devaya Namah",
}

COLOR_BY_MOON_SIGN = {
    0:"Red",1:"White",2:"Green",3:"Silver",4:"Golden",5:"Brown",
    6:"Blue",7:"Maroon",8:"Yellow",9:"Black",10:"Indigo",11:"Sea Green",
}

GEM_BY_PLANET = {
    "Sun":"Ruby","Moon":"Pearl","Mars":"Red Coral","Mercury":"Emerald",
    "Jupiter":"Yellow Sapphire","Venus":"Diamond","Saturn":"Blue Sapphire",
    "Rahu":"Hessonite (Gomed)","Ketu":"Cat's Eye (Lehsunia)",
}

TIME_BY_HOUSE = {
    1:"6–8 AM",2:"8–10 AM",3:"10–11 AM",4:"11 AM–12 PM",
    5:"12–1 PM",6:"1–2 PM",7:"2–3 PM",8:"3–5 PM",
    9:"5–6 PM",10:"6–7 PM",11:"7–8 PM",12:"8–9 PM",
}

DIR_BY_SUN_HOUSE = {
    1:"East",2:"SE",3:"South",4:"SW",5:"West",6:"NW",
    7:"North",8:"NE",9:"East",10:"SE",11:"South",12:"SW",
}

WEEKDAY_RULERS = ["Moon","Mars","Mercury","Jupiter","Venus","Saturn","Sun"]  # Mon–Sun


def _all_positions(jd):
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    out = {}
    for name, pid in PLANET_IDS.items():
        d   = swe.calc_ut(jd, pid, FLAGS)
        lon = d[0][0] % 360
        spd = d[0][3]
        if name == "Rahu":
            ketu_lon = (lon + 180) % 360
            out["Ketu"] = dict(
                sign_idx=int(ketu_lon/30), degree=ketu_lon%30,
                retrograde=True, nakshatra=NAKSHATRA_NAMES[int(ketu_lon/NAK_DIV)%27]
            )
        out[name] = dict(
            sign_idx=int(lon/30), degree=lon%30,
            retrograde=spd < 0, nakshatra=NAKSHATRA_NAMES[int(lon/NAK_DIV)%27]
        )
    return out


def _strength(pname, sign_idx):
    sno = sign_idx + 1
    if EXALTATION.get(pname)   == sno: return "Exalted",      +3
    if DEBILITATION.get(pname) == sno: return "Debilitated",  -2
    if sno in OWN_SIGNS.get(pname,[]): return "Own Sign",     +2
    return "Neutral", 0


def _house(planet_sign, lagna_sign):
    return ((planet_sign - lagna_sign) % 12) + 1


def _clamp_stars(raw):
    return max(1.0, min(5.0, raw))


def _stars_str(v):
    r = round(_clamp_stars(v))
    return "★"*r + "☆"*(5-r)


def generate_horoscope(sign_idx: int) -> dict:
    """
    Generate fully dynamic horoscope for zodiac sign 0=Aries…11=Pisces.
    Everything derived from live Swiss Ephemeris positions.
    """
    jd  = _jd_now()
    pan = _panchang_at(jd)
    pos = _all_positions(jd)

    sign_name   = RASHI_EN[sign_idx]
    moon_nak    = NAKSHATRA_NAMES[int(pan["moon"] / NAK_DIV) % 27]
    tithi_q     = TITHI_QUALITY.get(pan["tithi_idx"], 0)
    nak_q       = NAKSHATRA_QUALITY.get(moon_nak, 0)
    weekday_lord= WEEKDAY_RULERS[datetime.now().weekday()]

    # ── Analyse every planet's house + net influence ──────────────
    analysis = {}
    for pname, pdata in pos.items():
        if pname not in PLANET_KEYWORDS:
            continue
        house = _house(pdata["sign_idx"], sign_idx)
        str_label, str_score = _strength(pname, pdata["sign_idx"])
        nature = PLANET_NATURE.get(pname, 0)
        retro  = pdata["retrograde"]

        # Base net score
        net = nature + str_score
        if retro:
            net -= 0.5   # retrograde weakens forward results

        # House amplifiers
        if house in (1,4,7,10):   net *= 1.4   # kendras
        elif house in (2,5,9,11): net *= 1.1   # trikonas & upachayas
        elif house in (6,8,12):   net *= 0.8   # dusthanas

        analysis[pname] = {
            "house":     house,
            "sign":      RASHI_EN[pdata["sign_idx"]],
            "strength":  str_label,
            "retrograde":retro,
            "domain":    HOUSE_DOMAIN.get(house,""),
            "keyword":   PLANET_KEYWORDS[pname],
            "nakshatra": pdata["nakshatra"],
            "net":       round(net, 2),
        }

    def domain_score(houses):
        s = sum(analysis[p]["net"] for p in analysis if analysis[p]["house"] in houses)
        return _clamp_stars(3 + s * 0.4)

    overall_raw   = sum(a["net"] for a in analysis.values()) + tithi_q + nak_q
    overall_score = _clamp_stars(3 + overall_raw * 0.2)
    love_score    = domain_score([7,5,2])
    career_score  = domain_score([10,6,11])
    health_score  = domain_score([1,6,8])
    finance_score = domain_score([2,11,9])
    luck_score    = domain_score([9,5,1])

    # ── Natural language — assembled from planet data, not templates ──

    # Top 3 strongest influences
    top3 = sorted(analysis.items(), key=lambda x: abs(x[1]["net"]), reverse=True)[:3]

    overview_sentences = []
    for pname, pa in top3:
        s_txt = {
            "Exalted":     f"{pname} reaches its peak strength",
            "Own Sign":    f"{pname} is powerfully placed in its own sign",
            "Debilitated": f"{pname} is in a weakened state",
            "Neutral":     f"{pname} moves through",
        }.get(pa["strength"], f"{pname} transits")
        retro_txt = ", moving retrograde (inward reflection)" if pa["retrograde"] else ""
        overview_sentences.append(
            f"{s_txt}{retro_txt} in {pa['sign']}, illuminating your {pa['house']}th house "
            f"of {pa['domain']} — bringing themes of {pa['keyword']}."
        )

    tithi_txt = (
        f"Today's {pan['paksha']} paksha {TITHI_NAMES[pan['tithi_idx']]} tithi "
        + ("creates an auspicious backdrop for initiative and new starts."
           if tithi_q > 0 else
           "calls for patience, reflection and avoiding major decisions."
           if tithi_q < 0 else
           "supports steady, grounded action without extremes.")
    )
    moon_txt = (
        f"The Moon journeys through {moon_nak} nakshatra, "
        + ("amplifying intuition, emotional clarity and receptive energy."
           if nak_q > 0 else
           "stirring restlessness — ground yourself before important conversations."
           if nak_q < 0 else
           "inviting adaptability and mindful awareness throughout the day.")
    )
    overview = " ".join(overview_sentences) + " " + tithi_txt + " " + moon_txt

    # Love — 7th, 5th, 2nd house planets
    lp = {pn: pa for pn, pa in analysis.items() if pa["house"] in (7,5,2)}
    if lp:
        lp_txt = ". ".join(
            f"{pn} in house {pa['house']} ({pa['domain']}) {'supports' if pa['net']>=0 else 'strains'} relationships through {pa['keyword']}"
            for pn, pa in lp.items()
        ) + ". "
    else:
        lp_txt = "No major planet directly aspects your relationship houses today. "

    if love_score >= 4:
        lp_txt += "This is a genuinely favourable day for love — express feelings openly and nurture your bonds."
    elif love_score <= 2:
        lp_txt += "Tensions are possible in close relationships. Pause before reacting and choose compassion over correctness."
    else:
        lp_txt += "Maintain harmony through small, consistent gestures of care and attention."

    # Career — 10th, 6th, 11th house planets
    cp = {pn: pa for pn, pa in analysis.items() if pa["house"] in (10,6,11)}
    if cp:
        cp_txt = ". ".join(
            f"{pn} activating house {pa['house']} ({pa['domain']}) {'boosts' if pa['net']>=0 else 'complicates'} professional matters via {pa['keyword']}"
            for pn, pa in cp.items()
        ) + ". "
    else:
        cp_txt = "Career houses are relatively undisturbed by transits today. "

    if career_score >= 4:
        cp_txt += "A strong day for visibility and professional decisions — act with confidence."
    elif career_score <= 2:
        cp_txt += "Avoid signing contracts or making big career changes. Complete existing tasks carefully."
    else:
        cp_txt += "Methodical, consistent effort produces the best results in work matters today."

    # Health — 1st, 6th, 8th house planets
    hp = {pn: pa for pn, pa in analysis.items() if pa["house"] in (1,6,8)}
    if hp:
        hp_txt = ". ".join(
            f"{pn} in house {pa['house']} ({pa['domain']}) {'energises' if pa['net']>=0 else 'challenges'} wellbeing through {pa['keyword']}"
            for pn, pa in hp.items()
        ) + ". "
    else:
        hp_txt = "No strong planetary pressure on health houses today. "

    if health_score >= 4:
        hp_txt += "Vitality is high — leverage this for exercise, outdoor activity and creative work."
    elif health_score <= 2:
        hp_txt += "Rest is essential. Avoid overexertion and pay attention to digestive and nervous system signals."
    else:
        hp_txt += "Maintain your routine. Morning pranayama or yoga will support sustained energy levels."

    # ── Lucky indicators — derived from live data ─────────────────
    moon_sign_idx = int(pan["moon"] / 30)
    lucky_number  = ((moon_sign_idx + pan["tithi_idx"] + sign_idx) % 9) + 1
    lucky_color   = COLOR_BY_MOON_SIGN[moon_sign_idx % 12]

    sun_house     = analysis.get("Sun", {}).get("house", 1)
    best_time     = TIME_BY_HOUSE.get(sun_house, "Morning")
    best_dir      = DIR_BY_SUN_HOUSE.get(sun_house, "East")

    # Strongest benefic planet for gemstone
    benefics = [(pn, pa) for pn, pa in analysis.items() if PLANET_NATURE.get(pn,0) > 0]
    best_benefic = max(benefics, key=lambda x: x[1]["net"], default=("Jupiter", {}))
    lucky_gem = GEM_BY_PLANET.get(best_benefic[0], "Yellow Sapphire")

    mantra = NAK_MANTRAS.get(moon_nak, "Om Namah Shivaya")

    dom_house = max(analysis.values(), key=lambda x: abs(x["net"]), default={"house":9})["house"]
    tip = HOUSE_TIP.get(dom_house, "Act with dharma and sincerity today.")

    # Compatible signs: 5th and 9th from sign (trine), plus 7th (opposite)
    compat_signs = [
        RASHI_EN[(sign_idx + 4) % 12],
        RASHI_EN[(sign_idx + 8) % 12],
        RASHI_EN[(sign_idx + 6) % 12],
    ]

    return {
        "sign":           sign_name,
        "sign_idx":       sign_idx,
        "tithi":          TITHI_NAMES[pan["tithi_idx"]],
        "paksha":         pan["paksha"],
        "moon_nakshatra": moon_nak,
        "weekday_lord":   weekday_lord,

        "overview": overview,
        "love":     lp_txt,
        "career":   cp_txt,
        "health":   hp_txt,

        "scores": {
            "overall":  round(overall_score, 1),
            "love":     round(love_score, 1),
            "career":   round(career_score, 1),
            "health":   round(health_score, 1),
            "finance":  round(finance_score, 1),
            "luck":     round(luck_score, 1),
        },
        "stars": {
            "overall":  _stars_str(overall_score),
            "love":     _stars_str(love_score),
            "career":   _stars_str(career_score),
            "health":   _stars_str(health_score),
            "finance":  _stars_str(finance_score),
            "luck":     _stars_str(luck_score),
        },

        "lucky_number":  lucky_number,
        "lucky_color":   lucky_color,
        "lucky_gem":     lucky_gem,
        "best_time":     best_time,
        "best_dir":      best_dir,
        "ruling_planet": weekday_lord,
        "mantra":        mantra,
        "tip":           tip,
        "compat_signs":  compat_signs,

        "planet_positions": [
            {
                "name":      pn,
                "sign":      pa["sign"],
                "house":     pa["house"],
                "strength":  pa["strength"],
                "retrograde":pa["retrograde"],
                "nakshatra": pa["nakshatra"],
                "domain":    pa["domain"],
                "net":       pa["net"],
            }
            for pn, pa in analysis.items()
        ],
    }

'''
"""
festival_engine.py — Tithi-based Hindu Festival Engine + Dynamic Horoscope Engine
All festivals computed from live Swiss Ephemeris positions. Zero hardcoded Gregorian dates.
Horoscope text generated from real planet transits, house positions, strengths.
"""

import swisseph as swe
from datetime import datetime, timedelta, timezone

def get_ist_now():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)


from math import floor

swe.set_ephe_path('.')
swe.set_sid_mode(swe.SIDM_LAHIRI)

IST_OFFSET = 5.5
NAK_DIV    = 360 / 27  # 13.333...°

# ═══════════════════════════════════════════════════════════════
# REFERENCE DATA
# ═══════════════════════════════════════════════════════════════

TITHI_NAMES = [
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami",
    "Shashthi","Saptami","Ashtami","Navami","Dashami",
    "Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Purnima",
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami",
    "Shashthi","Saptami","Ashtami","Navami","Dashami",
    "Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Amavasya",
]

NAKSHATRA_NAMES = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
    "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha",
    "Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha",
    "Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
    "Uttara Bhadrapada","Revati",
]

RASHI_NAMES = [
    "Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya",
    "Tula","Vrischika","Dhanu","Makara","Kumbha","Meena",
]

RASHI_EN = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces",
]

YOGA_NAMES = [
    "Vishkumbha","Preeti","Ayushman","Saubhagya","Shobhana",
    "Atiganda","Sukarma","Dhriti","Shoola","Ganda","Vriddhi",
    "Dhruva","Vyaghata","Harshana","Vajra","Siddhi","Vyatipata",
    "Variyana","Parigha","Shiva","Siddha","Sadhya","Shubha",
    "Shukla","Brahma","Indra","Vaidhriti",
]

KARANA_NAMES = ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"]

# ═══════════════════════════════════════════════════════════════
# FESTIVAL RULES — 100% tithi / nakshatra / solar-ingress based
# paksha : "Shukla" | "Krishna" | "any"
# tithi  : 1-15 within the paksha (1=Pratipada … 15=Purnima/Amavasya)
# month  : solar rashi index 1-12 (Mesha=1…Meena=12) or None=any
# nakshatra : required Moon nakshatra or None
# sun_ingress: True = festival fires on first day Sun enters `month` sign
# ═══════════════════════════════════════════════════════════════
FESTIVAL_RULES = [
    # ── Shukla Paksha ────────────────────────────────────────────
    dict(paksha="Shukla",  tithi=1,  month=None, name="Shukla Pratipada",
         icon="🌒", desc="First day of waxing moon — auspicious for new beginnings",
         tag="vrat", remedies="Start new ventures, offer flowers to Devi"),

    dict(paksha="Shukla",  tithi=4,  month=4,  name="Ganesh Chaturthi",
         icon="🐘", desc="Birth of Lord Ganesha — worship with modak and 21 durva blades",
         tag="major", remedies="Fast, offer modak, chant Ganpati Atharvashirsha 108×"),

    dict(paksha="Shukla",  tithi=4,  month=None, name="Vinayak Chaturthi",
         icon="🐘", desc="Monthly Ganesha worship — remove obstacles in all endeavours",
         tag="vrat", remedies="Offer modak and durva, chant Om Gam Ganapataye Namah"),

    dict(paksha="Shukla",  tithi=5,  month=10, name="Vasant Panchami",
         icon="🌼", desc="Saraswati Puja — goddess of learning, arts and wisdom worshipped in yellow",
         tag="major", remedies="Wear yellow, offer yellow flowers to Saraswati, begin new studies"),

    dict(paksha="Shukla",  tithi=6,  month=None, name="Skanda Sashti",
         icon="⚔️", desc="Worship of Lord Kartikeya (Murugan) — victory over inner demons",
         tag="festival", remedies="Fast, recite Kandha Sashti Kavacham, offer red flowers"),

    dict(paksha="Shukla",  tithi=7,  month=None, name="Sapta Tithi",
         icon="☀️", desc="Seventh lunar day — auspicious for Sun worship",
         tag="vrat", remedies="Offer water to Sun, recite Aditya Hridayam"),

    dict(paksha="Shukla",  tithi=8,  month=None, name="Durgashtami",
         icon="🔱", desc="Monthly Durga worship — invoke strength and protection",
         tag="vrat", remedies="Offer kumkum and red flowers to Durga, fast half-day"),

    dict(paksha="Shukla",  tithi=9,  month=None, name="Ram Navami",
         icon="🏹", desc="Birthday of Lord Rama — recite Ramcharitmanas, fast till evening",
         tag="major", remedies="Fast, recite Ramayana, offer tulsi and flowers to Ram"),

    dict(paksha="Shukla",  tithi=11, month=None, name="Ekadashi",
         icon="🌿", desc="Sacred fasting day of Lord Vishnu — most powerful day for moksha",
         tag="ekadashi", remedies="Fast on Ekadashi, chant Vishnu Sahasranama, stay awake at night"),

    dict(paksha="Shukla",  tithi=12, month=None, name="Dwadashi (Vaishnava)",
         icon="🪷", desc="Ekadashi parana day — break fast with tulsi water at auspicious time",
         tag="vrat", remedies="Break Ekadashi fast correctly, offer tulsi to Vishnu"),

    dict(paksha="Shukla",  tithi=13, month=None, name="Pradosh Vrat",
         icon="🕉️", desc="Auspicious evening vrat for Lord Shiva — performed at dusk",
         tag="vrat", remedies="Visit Shiva temple at dusk, offer bilva leaves, fast till evening"),

    dict(paksha="Shukla",  tithi=14, month=9,  name="Maha Shivaratri",
         icon="🕉️", desc="Great night of Lord Shiva — most sacred night of the entire year",
         tag="major", remedies="All-night vigil, fast, bathe Shivalinga with milk, bilva, honey"),

    dict(paksha="Shukla",  tithi=14, month=None, name="Shiva Chaturdashi",
         icon="🕉️", desc="Monthly Masik Shivaratri — worship Shiva at midnight",
         tag="vrat", remedies="Fast, offer bilva, light lamps for Shiva at midnight"),

    dict(paksha="Shukla",  tithi=15, month=None, name="Purnima",
         icon="🌕", desc="Full Moon — sacred for ancestor rites, charity and sattvic practices",
         tag="purnima", remedies="Donate, bathe in sacred river, observe fast, light lamps"),

    dict(paksha="Shukla",  tithi=15, month=1,  name="Holi Purnima (Holika Dahan)",
         icon="🎨", desc="Holika Dahan — sacred bonfire symbolising victory of devotion over evil",
         tag="major", remedies="Perform Holika puja, walk around fire 3×, pray for protection"),

    dict(paksha="Shukla",  tithi=15, month=2,  name="Buddha Purnima",
         icon="☸️", desc="Birth of Gautama Buddha — practice ahimsa, compassion and dana",
         tag="festival", remedies="Observe silence, donate food, practise loving-kindness meditation"),

    dict(paksha="Shukla",  tithi=15, month=3,  name="Guru Purnima",
         icon="🪷", desc="Honour your Guru — offer gratitude to teachers and spiritual lineage",
         tag="major", remedies="Serve your guru, study scriptures, donate to teachers"),

    dict(paksha="Shukla",  tithi=15, month=5,  name="Sharad Purnima",
         icon="🌕", desc="Moon at its fullest — prepare kheer, offer to moonlight overnight",
         tag="major", remedies="Prepare rice kheer, place under moonlight, consume at sunrise"),

    dict(paksha="Shukla",  tithi=15, month=6,  name="Kartik Purnima (Dev Deepawali)",
         icon="🪔", desc="Dev Deepawali — gods descend to bathe in Ganga, light lamps on river",
         tag="major", remedies="Light 108 diyas on river bank, take Kartik bath at sunrise"),

    dict(paksha="Shukla",  tithi=15, month=7,  name="Raksha Bandhan",
         icon="🧵", desc="Sacred sibling bond — sister ties rakhi for brother's protection",
         tag="major", remedies="Perform rakhi ceremony during auspicious muhurat, pray for sibling"),

    # ── Krishna Paksha ───────────────────────────────────────────
    dict(paksha="Krishna", tithi=4,  month=None, name="Sankashta Chaturthi",
         icon="🐘", desc="Monthly Ganesha vrat on Krishna Chaturthi — remove accumulated obstacles",
         tag="vrat", remedies="Fast until moon rise, offer modak, chant Sankat Nashan Ganesh Stotra"),

    dict(paksha="Krishna", tithi=8,  month=4,  name="Janmashtami",
         icon="🦚", desc="Birthday of Lord Krishna — midnight celebration, dahi-handi, bhajans",
         tag="major", remedies="Fast until midnight, perform Krishna puja, sing bhajans all night"),

    dict(paksha="Krishna", tithi=8,  month=None, name="Masik Ashtami (Kalashtami)",
         icon="🔱", desc="Monthly Bhairav worship — Kaal Bhairav is worshipped at night",
         tag="vrat", remedies="Fast, visit Bhairav temple at night, offer sesame oil lamps"),

    dict(paksha="Krishna", tithi=11, month=None, name="Ekadashi",
         icon="🌿", desc="Sacred fasting day of Lord Vishnu — equally powerful as Shukla Ekadashi",
         tag="ekadashi", remedies="Fast, chant Vishnu Sahasranama, sleep on floor, avoid rice"),

    dict(paksha="Krishna", tithi=13, month=None, name="Pradosh Vrat",
         icon="🕉️", desc="Evening Shiva worship — Shiva and Parvati are happy at this time",
         tag="vrat", remedies="Shiva puja at dusk, offer bilva and white flowers, fast till evening"),

    dict(paksha="Krishna", tithi=13, month=5,  name="Dhanteras",
         icon="💰", desc="Worship of Dhanvantari and Yama — buy metals for prosperity",
         tag="major", remedies="Light 13 diyas facing south, worship Lakshmi and Dhanvantari"),

    dict(paksha="Krishna", tithi=14, month=5,  name="Naraka Chaturdashi (Choti Diwali)",
         icon="🪔", desc="Victory over demon Narakasura — bathe before sunrise for liberation",
         tag="major", remedies="Bathe before sunrise with sesame oil, light lamps, pray to Yama"),

    dict(paksha="Krishna", tithi=14, month=None, name="Shiva Chaturdashi (Masik Shivaratri)",
         icon="🕉️", desc="Monthly Shiva worship night — Shiva is at his most accessible",
         tag="vrat", remedies="Fast, offer milk to Shivalinga at midnight, chant Om Namah Shivaya"),

    dict(paksha="Krishna", tithi=15, month=None, name="Amavasya",
         icon="🌑", desc="New Moon — most sacred day for Pitru tarpan and ancestor worship",
         tag="amavasya", remedies="Offer water tarpan to ancestors, donate in their name, light sesame lamps"),

    dict(paksha="Krishna", tithi=15, month=5,  name="Diwali (Lakshmi Puja)",
         icon="🪔", desc="Festival of lights — Goddess Lakshmi worshipped for wealth and prosperity",
         tag="major", remedies="Light clay diyas, perform Lakshmi-Ganesh puja at night, donate to poor"),

    dict(paksha="Krishna", tithi=15, month=6,  name="Kartik Amavasya",
         icon="🌑", desc="Sacred new moon in Kartik — light lamps on rivers for ancestors",
         tag="major", remedies="Light diyas on flowing water, offer tarpan to departed ancestors"),

    dict(paksha="Krishna", tithi=15, month=8,  name="Mahalaya Amavasya (Pitru Paksha End)",
         icon="🌑", desc="Final day of Pitru Paksha — most powerful day for ancestor worship",
         tag="major", remedies="Perform Shraddha and tarpan, donate food in ancestor's name"),

    # ── Nakshatra-based ──────────────────────────────────────────
    dict(paksha="any", tithi=None, month=None, nakshatra="Pushya",
         name="Pushya Nakshatra", icon="⭐",
         desc="Most auspicious nakshatra — ideal for beginning new work, buying gold, studies",
         tag="nakshatra", remedies="Begin important work, buy gold or property, visit temple"),

    dict(paksha="any", tithi=None, month=None, nakshatra="Rohini",
         name="Rohini Nakshatra", icon="🌸",
         desc="Moon's favourite nakshatra — excellent for agriculture, arts and relationships",
         tag="nakshatra", remedies="Plant seeds, begin creative projects, worship Moon"),

    dict(paksha="any", tithi=None, month=None, nakshatra="Hasta",
         name="Hasta Nakshatra", icon="✋",
         desc="Nakshatra of craftsmanship — ideal for trade, artisans and healing work",
         tag="nakshatra", remedies="Engage in skilled work, visit Surya temple"),

    # ── Solar Ingress (Sankranti) ────────────────────────────────
    dict(paksha="any", tithi=None, month=1,  sun_ingress=True,
         name="Mesha Sankranti (Vedic New Year)", icon="🌅",
         desc="Sun enters Aries — Vedic Solar New Year, most important Sankranti",
         tag="major", remedies="Bathe at sunrise, donate sesame, worship Surya facing East"),

    dict(paksha="any", tithi=None, month=10, sun_ingress=True,
         name="Makar Sankranti", icon="🪁",
         desc="Sun enters Capricorn — Uttarayan begins, harvest festival across India",
         tag="major", remedies="Take holy dip before sunrise, donate til-gur, fly kites"),

    dict(paksha="any", tithi=None, month=4,  sun_ingress=True,
         name="Karka Sankranti (Dakshinayan)", icon="☀️",
         desc="Sun enters Cancer — Dakshinayan begins, ancestors descend",
         tag="sankranti", remedies="Donate, observe fast, perform pitru tarpan"),

    dict(paksha="any", tithi=None, month=2,  sun_ingress=True,
         name="Vrishabha Sankranti", icon="☀️",
         desc="Sun enters Taurus — auspicious for land, agriculture and wealth",
         tag="sankranti", remedies="Donate cow's ghee, worship Lakshmi"),

    dict(paksha="any", tithi=None, month=None, sun_ingress=True,
         name="Masa Sankranti", icon="☀️",
         desc="Monthly solar ingress — Sun changes sign, auspicious for charity",
         tag="sankranti", remedies="Donate, bathe, pray to Surya Narayan"),
]

# ═══════════════════════════════════════════════════════════════
# EPHEMERIS HELPERS
# ═══════════════════════════════════════════════════════════════

# def _jd_now():
#     now = datetime.now(timezone.utc)
#     return swe.julday(now.year, now.month, now.day,
#                       now.hour + now.minute/60 + now.second/3600)

def _jd_now():
    now = get_ist_now()
    return swe.julday(
        now.year,
        now.month,
        now.day,
        now.hour + now.minute/60 + now.second/3600
    )

def _panchang_at(jd):
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun  = swe.calc_ut(jd, swe.SUN,  FLAGS)[0][0]
    moon = swe.calc_ut(jd, swe.MOON, FLAGS)[0][0]
    diff = (moon - sun) % 360
    tithi_idx = int(diff / 12)  # 0-29
    paksha    = "Shukla" if tithi_idx < 15 else "Krishna"
    tithi_no  = (tithi_idx % 15) + 1   # 1-15 in each paksha
    nak_idx   = int(moon / NAK_DIV) % 27
    sun_sign  = int(sun / 30) + 1      # 1-12
    return {
        "tithi_idx":  tithi_idx,
        "tithi_no":   tithi_no,
        "paksha":     paksha,
        "nak_name":   NAKSHATRA_NAMES[nak_idx],
        "sun_sign":   sun_sign,
        "sun":        sun,
        "moon":       moon,
        "diff":       diff,
    }

def _jd_to_date(jd):
    y, m, d, _ = swe.revjul(jd)
    return datetime(int(y), int(m), int(d))

def _match_rule(rule, pan, prev_sun_sign):
    """Returns True when festival rule matches today's panchang."""
    # --- tithi check ---
    if rule.get("tithi") is not None:
        if pan["tithi_no"] != rule["tithi"]:
            return False
        rp = rule.get("paksha", "any")
        if rp != "any" and pan["paksha"] != rp:
            return False

    # --- nakshatra check ---
    if rule.get("nakshatra"):
        if pan["nak_name"] != rule["nakshatra"]:
            return False

    # --- solar month / ingress check ---
    if rule.get("sun_ingress"):
        if rule.get("month"):
            # fires on first day sun is in that sign (ingress day)
            if pan["sun_sign"] != rule["month"] or prev_sun_sign == rule["month"]:
                return False
        else:
            # any ingress
            if pan["sun_sign"] == prev_sun_sign:
                return False
    elif rule.get("month") is not None:
        if pan["sun_sign"] != rule["month"]:
            return False

    return True

# ═══════════════════════════════════════════════════════════════
# PUBLIC — FESTIVAL API
# ═══════════════════════════════════════════════════════════════

def get_festivals_range(days: int = 60) -> list:
    results = []
    seen    = set()
    jd_start = _jd_now()
    prev_sun_sign = _panchang_at(jd_start - 1)["sun_sign"]

    for i in range(days):
        jd  = jd_start + i
        pan = _panchang_at(jd)
        dt  = _jd_to_date(jd)
        date_str = dt.strftime("%Y-%m-%d")
        is_today = (i == 0)

        for rule in FESTIVAL_RULES:
            if _match_rule(rule, pan, prev_sun_sign):
                key = (date_str, rule["name"])
                if key not in seen:
                    seen.add(key)
                    results.append({
                        "date":      date_str,
                        "display":   "Today" if is_today else dt.strftime("%d %b"),
                        "name":      rule["name"],
                        "icon":      rule["icon"],
                        "desc":      rule["desc"],
                        "tag":       rule["tag"],
                        "remedies":  rule.get("remedies", ""),
                        "paksha":    pan["paksha"],
                        "tithi":     TITHI_NAMES[pan["tithi_idx"]],
                        "nakshatra": pan["nak_name"],
                        "is_today":  is_today,
                    })
        prev_sun_sign = pan["sun_sign"]

    results.sort(key=lambda x: x["date"])
    return results


def get_today_festivals() -> list:
    return [f for f in get_festivals_range(1) if f["is_today"]]


def get_upcoming_festivals(limit: int = 12) -> list:
    return get_festivals_range(90)[:limit]


# ═══════════════════════════════════════════════════════════════
# DYNAMIC HOROSCOPE ENGINE
# Fully derived from live planetary transits — no static text
# ═══════════════════════════════════════════════════════════════

PLANET_IDS = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus":   swe.VENUS,
    "Mars":    swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn":  swe.SATURN,
    "Rahu":    swe.TRUE_NODE,
}

# Exaltation / debilitation / own sign — 1-based sign numbers
EXALTATION   = dict(Sun=1,  Moon=2,  Mars=10, Mercury=6,  Jupiter=4,  Venus=12, Saturn=7)
DEBILITATION = dict(Sun=7,  Moon=8,  Mars=4,  Mercury=12, Jupiter=10, Venus=6,  Saturn=1)
OWN_SIGNS    = dict(Sun=[5],Moon=[4],Mars=[1,8],Mercury=[3,6],Jupiter=[9,12],Venus=[2,7],Saturn=[10,11])

# Natural benefic/malefic
PLANET_NATURE = {
    "Jupiter": +2, "Venus": +2, "Moon": +1, "Mercury": +1,
    "Sun":  0, "Mars": -1, "Saturn": -2, "Rahu": -1, "Ketu": -1,
}

PLANET_KEYWORDS = {
    "Sun":     "authority, vitality, recognition, father, government",
    "Moon":    "emotions, intuition, mother, public, nourishment",
    "Mercury": "intellect, communication, business, logic, skin",
    "Venus":   "love, beauty, arts, marriage, luxury",
    "Mars":    "courage, energy, siblings, conflict, land",
    "Jupiter": "wisdom, expansion, children, wealth, spirituality",
    "Saturn":  "karma, discipline, delay, service, longevity",
    "Rahu":    "obsession, foreign, technology, illusion, ambition",
    "Ketu":    "detachment, spirituality, past karma, liberation",
}

HOUSE_DOMAIN = {
    1:"self and personality",   2:"wealth and family",
    3:"courage and communication", 4:"home and mother",
    5:"children and intelligence", 6:"health and enemies",
    7:"marriage and partnerships", 8:"transformation and longevity",
    9:"luck and dharma",          10:"career and status",
    11:"gains and fulfilment",    12:"spirituality and losses",
}

NAKSHATRA_QUALITY = {
    "Ashwini":1,"Bharani":-1,"Krittika":0,"Rohini":2,"Mrigashira":1,
    "Ardra":-1,"Punarvasu":2,"Pushya":3,"Ashlesha":-1,"Magha":-1,
    "Purva Phalguni":-1,"Uttara Phalguni":2,"Hasta":2,"Chitra":1,
    "Swati":1,"Vishakha":-1,"Anuradha":2,"Jyeshtha":-1,"Mula":-1,
    "Purva Ashadha":-1,"Uttara Ashadha":2,"Shravana":2,"Dhanishta":1,
    "Shatabhisha":-1,"Purva Bhadrapada":-1,"Uttara Bhadrapada":2,"Revati":2,
}

TITHI_QUALITY = {
    0:+2, 1:+2, 2:+2, 4:+1, 5:+1, 10:+2, 11:+1, 14:+2,  # Pratipada,Dwi,Tri,Panch,Shash,Ekad,Dwad,Purnima
    3:-1, 7:-1, 8:-1, 12:-1, 13:-1, 29:-2,                # Chauth,Asht,Navam,Trayd,Chaturd,Amavasya
}

HOUSE_TIP = {
    1:"Focus on personal presentation and first impressions. Start something new for yourself.",
    2:"Review finances and savings. Reconnect with family over a meal.",
    3:"Excellent for writing, speaking, calls and short journeys. Sign documents.",
    4:"Spend time at home. Property and mother-related matters are highlighted.",
    5:"Creative projects, speculative investments and children are in focus.",
    6:"Address health issues promptly. Settle outstanding debts or conflicts early.",
    7:"Partnership and marriage matters deserve attention. Compromise openly.",
    8:"Avoid risky investments. Day favours inner transformation and occult study.",
    9:"Seek guidance from elders or teachers. Long-distance travel is auspicious.",
    10:"Career decisions bring recognition. Connect with senior colleagues.",
    11:"Networking and unexpected income. Meet friends and pursue social goals.",
    12:"Meditate and retreat inward. Foreign connections or hospital visits possible.",
}

NAK_MANTRAS = {
    "Ashwini":"Om Ashwinau Tejase Namah","Bharani":"Om Yama Dharmarajaya Namah",
    "Krittika":"Om Agni Devaya Namah","Rohini":"Om Brahma Devaya Namah",
    "Mrigashira":"Om Soma Devaya Namah","Ardra":"Om Rudraya Namah",
    "Punarvasu":"Om Adityaya Namah","Pushya":"Om Brihaspataye Namah",
    "Ashlesha":"Om Sarpebhyo Namah","Magha":"Om Pitribhyo Namah",
    "Purva Phalguni":"Om Bhagaya Namah","Uttara Phalguni":"Om Arya Devaya Namah",
    "Hasta":"Om Savitri Devaya Namah","Chitra":"Om Vishwakarma Devaya Namah",
    "Swati":"Om Vayu Devaya Namah","Vishakha":"Om Indra Agnibhyam Namah",
    "Anuradha":"Om Mitra Devaya Namah","Jyeshtha":"Om Indra Devaya Namah",
    "Mula":"Om Nirriti Devaya Namah","Purva Ashadha":"Om Jala Devaya Namah",
    "Uttara Ashadha":"Om Vishwe Devebhyo Namah","Shravana":"Om Vishnu Devaya Namah",
    "Dhanishta":"Om Ashta Vasebhyo Namah","Shatabhisha":"Om Varuna Devaya Namah",
    "Purva Bhadrapada":"Om Aja Ekapadaya Namah",
    "Uttara Bhadrapada":"Om Ahir Budhanyaya Namah","Revati":"Om Pusha Devaya Namah",
}

COLOR_BY_MOON_SIGN = {
    0:"Red",1:"White",2:"Green",3:"Silver",4:"Golden",5:"Brown",
    6:"Blue",7:"Maroon",8:"Yellow",9:"Black",10:"Indigo",11:"Sea Green",
}

GEM_BY_PLANET = {
    "Sun":"Ruby","Moon":"Pearl","Mars":"Red Coral","Mercury":"Emerald",
    "Jupiter":"Yellow Sapphire","Venus":"Diamond","Saturn":"Blue Sapphire",
    "Rahu":"Hessonite (Gomed)","Ketu":"Cat's Eye (Lehsunia)",
}

TIME_BY_HOUSE = {
    1:"6–8 AM",2:"8–10 AM",3:"10–11 AM",4:"11 AM–12 PM",
    5:"12–1 PM",6:"1–2 PM",7:"2–3 PM",8:"3–5 PM",
    9:"5–6 PM",10:"6–7 PM",11:"7–8 PM",12:"8–9 PM",
}

DIR_BY_SUN_HOUSE = {
    1:"East",2:"SE",3:"South",4:"SW",5:"West",6:"NW",
    7:"North",8:"NE",9:"East",10:"SE",11:"South",12:"SW",
}

WEEKDAY_RULERS = ["Moon","Mars","Mercury","Jupiter","Venus","Saturn","Sun"]  # Mon–Sun


def _all_positions(jd):
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    out = {}
    for name, pid in PLANET_IDS.items():
        d   = swe.calc_ut(jd, pid, FLAGS)
        lon = d[0][0] % 360
        spd = d[0][3]
        if name == "Rahu":
            ketu_lon = (lon + 180) % 360
            out["Ketu"] = dict(
                sign_idx=int(ketu_lon/30), degree=ketu_lon%30,
                retrograde=True, nakshatra=NAKSHATRA_NAMES[int(ketu_lon/NAK_DIV)%27]
            )
        out[name] = dict(
            sign_idx=int(lon/30), degree=lon%30,
            retrograde=spd < 0, nakshatra=NAKSHATRA_NAMES[int(lon/NAK_DIV)%27]
        )
    return out


def _strength(pname, sign_idx):
    sno = sign_idx + 1
    if EXALTATION.get(pname)   == sno: return "Exalted",      +3
    if DEBILITATION.get(pname) == sno: return "Debilitated",  -2
    if sno in OWN_SIGNS.get(pname,[]): return "Own Sign",     +2
    return "Neutral", 0


def _house(planet_sign, lagna_sign):
    return ((planet_sign - lagna_sign) % 12) + 1


def _ordinal(n):
    """Return '1st', '2nd', '3rd', '4th' … '12th'."""
    suffix = {1:"st", 2:"nd", 3:"rd"}.get(n if n < 20 else n % 10, "th")
    return f"{n}{suffix}"


def _clamp_stars(raw):
    return max(1.0, min(5.0, raw))


def _stars_str(v):
    r = round(_clamp_stars(v))
    return "★"*r + "☆"*(5-r)


def generate_horoscope(sign_idx: int) -> dict:
    """
    Generate fully dynamic horoscope for zodiac sign 0=Aries…11=Pisces.
    Everything derived from live Swiss Ephemeris positions.
    """
    jd  = _jd_now()
    pan = _panchang_at(jd)
    pos = _all_positions(jd)

    sign_name   = RASHI_EN[sign_idx]
    moon_nak    = NAKSHATRA_NAMES[int(pan["moon"] / NAK_DIV) % 27]
    tithi_q     = TITHI_QUALITY.get(pan["tithi_idx"], 0)
    nak_q       = NAKSHATRA_QUALITY.get(moon_nak, 0)
    #weekday_lord= WEEKDAY_RULERS[datetime.now().weekday()]
    weekday_lord = WEEKDAY_RULERS[get_ist_now().weekday()]
    
    # ── Analyse every planet's house + net influence ──────────────
    analysis = {}
    for pname, pdata in pos.items():
        if pname not in PLANET_KEYWORDS:
            continue
        house = _house(pdata["sign_idx"], sign_idx)
        str_label, str_score = _strength(pname, pdata["sign_idx"])
        nature = PLANET_NATURE.get(pname, 0)
        retro  = pdata["retrograde"]

        # Base net score
        net = nature + str_score
        if retro:
            net -= 0.5   # retrograde weakens forward results

        # House amplifiers
        if house in (1,4,7,10):   net *= 1.4   # kendras
        elif house in (2,5,9,11): net *= 1.1   # trikonas & upachayas
        elif house in (6,8,12):   net *= 0.8   # dusthanas

        analysis[pname] = {
            "house":     house,
            "sign":      RASHI_EN[pdata["sign_idx"]],
            "strength":  str_label,
            "retrograde":retro,
            "domain":    HOUSE_DOMAIN.get(house,""),
            "keyword":   PLANET_KEYWORDS[pname],
            "nakshatra": pdata["nakshatra"],
            "net":       round(net, 2),
        }

    def domain_score(houses):
        s = sum(analysis[p]["net"] for p in analysis if analysis[p]["house"] in houses)
        return _clamp_stars(3 + s * 0.4)

    overall_raw   = sum(a["net"] for a in analysis.values()) + tithi_q + nak_q
    overall_score = _clamp_stars(3 + overall_raw * 0.2)
    love_score    = domain_score([7,5,2])
    career_score  = domain_score([10,6,11])
    health_score  = domain_score([1,6,8])
    finance_score = domain_score([2,11,9])
    luck_score    = domain_score([9,5,1])

    # ── Natural language — assembled from planet data, not templates ──

    # Top 3 strongest influences
    top3 = sorted(analysis.items(), key=lambda x: abs(x[1]["net"]), reverse=True)[:3]

    overview_sentences = []
    for pname, pa in top3:
        s_txt = {
            "Exalted":     f"{pname} reaches its peak strength",
            "Own Sign":    f"{pname} is powerfully placed in its own sign",
            "Debilitated": f"{pname} is in a weakened state",
            "Neutral":     f"{pname} moves through",
        }.get(pa["strength"], f"{pname} transits")
        retro_txt = ", moving retrograde (inward reflection)" if pa["retrograde"] else ""
        overview_sentences.append(
            f"{s_txt}{retro_txt} in {pa['sign']}, illuminating your {pa['house']}th house "
            f"of {pa['domain']} — bringing themes of {pa['keyword']}."
        )

    tithi_txt = (
        f"Today's {pan['paksha']} paksha {TITHI_NAMES[pan['tithi_idx']]} tithi "
        + ("creates an auspicious backdrop for initiative and new starts."
           if tithi_q > 0 else
           "calls for patience, reflection and avoiding major decisions."
           if tithi_q < 0 else
           "supports steady, grounded action without extremes.")
    )
    moon_txt = (
        f"The Moon journeys through {moon_nak} nakshatra, "
        + ("amplifying intuition, emotional clarity and receptive energy."
           if nak_q > 0 else
           "stirring restlessness — ground yourself before important conversations."
           if nak_q < 0 else
           "inviting adaptability and mindful awareness throughout the day.")
    )
    overview = " ".join(overview_sentences) + " " + tithi_txt + " " + moon_txt

    # Love — 7th, 5th, 2nd house planets
    lp = {pn: pa for pn, pa in analysis.items() if pa["house"] in (7,5,2)}
    if lp:
        lp_txt = ". ".join(
            f"{pn} in house {pa['house']} ({pa['domain']}) {'supports' if pa['net']>=0 else 'strains'} relationships through {pa['keyword']}"
            for pn, pa in lp.items()
        ) + ". "
    else:
        lp_txt = "No major planet directly aspects your relationship houses today. "

    if love_score >= 4:
        lp_txt += "This is a genuinely favourable day for love — express feelings openly and nurture your bonds."
    elif love_score <= 2:
        lp_txt += "Tensions are possible in close relationships. Pause before reacting and choose compassion over correctness."
    else:
        lp_txt += "Maintain harmony through small, consistent gestures of care and attention."

    # Career — 10th, 6th, 11th house planets
    cp = {pn: pa for pn, pa in analysis.items() if pa["house"] in (10,6,11)}
    if cp:
        cp_txt = ". ".join(
            f"{pn} activating house {pa['house']} ({pa['domain']}) {'boosts' if pa['net']>=0 else 'complicates'} professional matters via {pa['keyword']}"
            for pn, pa in cp.items()
        ) + ". "
    else:
        cp_txt = "Career houses are relatively undisturbed by transits today. "

    if career_score >= 4:
        cp_txt += "A strong day for visibility and professional decisions — act with confidence."
    elif career_score <= 2:
        cp_txt += "Avoid signing contracts or making big career changes. Complete existing tasks carefully."
    else:
        cp_txt += "Methodical, consistent effort produces the best results in work matters today."

    # Health — 1st, 6th, 8th house planets
    hp = {pn: pa for pn, pa in analysis.items() if pa["house"] in (1,6,8)}
    if hp:
        hp_txt = ". ".join(
            f"{pn} in house {pa['house']} ({pa['domain']}) {'energises' if pa['net']>=0 else 'challenges'} wellbeing through {pa['keyword']}"
            for pn, pa in hp.items()
        ) + ". "
    else:
        hp_txt = "No strong planetary pressure on health houses today. "

    if health_score >= 4:
        hp_txt += "Vitality is high — leverage this for exercise, outdoor activity and creative work."
    elif health_score <= 2:
        hp_txt += "Rest is essential. Avoid overexertion and pay attention to digestive and nervous system signals."
    else:
        hp_txt += "Maintain your routine. Morning pranayama or yoga will support sustained energy levels."

    # ── Lucky indicators — derived from live data ─────────────────
    moon_sign_idx = int(pan["moon"] / 30)
    lucky_number  = ((moon_sign_idx + pan["tithi_idx"] + sign_idx) % 9) + 1
    lucky_color   = COLOR_BY_MOON_SIGN[moon_sign_idx % 12]

    sun_house     = analysis.get("Sun", {}).get("house", 1)
    best_time     = TIME_BY_HOUSE.get(sun_house, "Morning")
    best_dir      = DIR_BY_SUN_HOUSE.get(sun_house, "East")

    # Strongest benefic planet for gemstone
    benefics = [(pn, pa) for pn, pa in analysis.items() if PLANET_NATURE.get(pn,0) > 0]
    best_benefic = max(benefics, key=lambda x: x[1]["net"], default=("Jupiter", {}))
    lucky_gem = GEM_BY_PLANET.get(best_benefic[0], "Yellow Sapphire")

    mantra = NAK_MANTRAS.get(moon_nak, "Om Namah Shivaya")

    dom_house = max(analysis.values(), key=lambda x: abs(x["net"]), default={"house":9})["house"]
    tip = HOUSE_TIP.get(dom_house, "Act with dharma and sincerity today.")

    # Compatible signs: 5th and 9th from sign (trine), plus 7th (opposite)
    compat_signs = [
        RASHI_EN[(sign_idx + 4) % 12],
        RASHI_EN[(sign_idx + 8) % 12],
        RASHI_EN[(sign_idx + 6) % 12],
    ]

    return {
        "sign":           sign_name,
        "sign_idx":       sign_idx,
        "tithi":          TITHI_NAMES[pan["tithi_idx"]],
        "paksha":         pan["paksha"],
        "moon_nakshatra": moon_nak,
        "weekday_lord":   weekday_lord,

        "overview": overview,
        "love":     lp_txt,
        "career":   cp_txt,
        "health":   hp_txt,

        "scores": {
            "overall":  round(overall_score, 1),
            "love":     round(love_score, 1),
            "career":   round(career_score, 1),
            "health":   round(health_score, 1),
            "finance":  round(finance_score, 1),
            "luck":     round(luck_score, 1),
        },
        "stars": {
            "overall":  _stars_str(overall_score),
            "love":     _stars_str(love_score),
            "career":   _stars_str(career_score),
            "health":   _stars_str(health_score),
            "finance":  _stars_str(finance_score),
            "luck":     _stars_str(luck_score),
        },

        "lucky_number":  lucky_number,
        "lucky_color":   lucky_color,
        "lucky_gem":     lucky_gem,
        "best_time":     best_time,
        "best_dir":      best_dir,
        "ruling_planet": weekday_lord,
        "mantra":        mantra,
        "tip":           tip,
        "compat_signs":  compat_signs,

        "planet_positions": [
            {
                "name":      pn,
                "sign":      pa["sign"],
                "house":     pa["house"],
                "strength":  pa["strength"],
                "retrograde":pa["retrograde"],
                "nakshatra": pa["nakshatra"],
                "domain":    pa["domain"],
                "net":       pa["net"],
            }
            for pn, pa in analysis.items()
        ],
    }
