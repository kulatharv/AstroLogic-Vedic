'''
import swisseph as swe
from datetime import datetime, timedelta
from math import floor
from astro_engine.cities import CITIES

swe.set_ephe_path(".")


swe.set_ephe_path('.')  # your ephemeris folder path
swe.set_sid_mode(swe.SIDM_LAHIRI)

NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira",
    "Ardra","Punarvasu","Pushya","Ashlesha","Magha",
    "Purva Phalguni","Uttara Phalguni","Hasta","Chitra",
    "Swati","Vishakha","Anuradha","Jyeshtha","Mula",
    "Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta",
    "Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"
]

TITHIS = [
    "Pratipada","Dvitiya","Tritiya","Chaturthi","Panchami",
    "Shashthi","Saptami","Ashtami","Navami","Dashami",
    "Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Purnima",
    "Pratipada","Dvitiya","Tritiya","Chaturthi","Panchami",
    "Shashthi","Saptami","Ashtami","Navami","Dashami",
    "Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Amavasya"
]

YOGAS = [f"Yoga {i}" for i in range(1,28)]
KARANAS = ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"]


def format_time(jd):
    frac = jd % 1
    hours = int(frac * 24)
    minutes = int((frac * 24 - hours) * 60)
    return f"{hours:02}:{minutes:02}"


def get_sun_times(jd, lat, lon):

    jd = float(jd)
    lat = float(lat)
    lon = float(lon)

    # geopos array required by Windows build
    geopos = (lon, lat, 0.0)

    # atmospheric values
    atpress = 0.0
    attemp = 0.0

    # Rise
    rise_flag = swe.CALC_RISE

    sunrise = swe.rise_trans(
        jd,
        swe.SUN,
        rise_flag,
        geopos,
        atpress,
        attemp
    )[1][0]

    # Set
    set_flag = swe.CALC_SET

    sunset = swe.rise_trans(
        jd,
        swe.SUN,
        set_flag,
        geopos,
        atpress,
        attemp
    )[1][0]

    return sunrise, sunset

def calculate_end_time(jd, target_angle, angle_func, step=0.01):
    test_jd = jd
    while True:
        test_jd += step
        if angle_func(test_jd) >= target_angle:
            return test_jd


def get_full_panchang(city):

    city_data = CITIES[city]
    lat = city_data["lat"]
    lon = city_data["lon"]

    now = datetime.now()
    timezone = 5.5  # IST

    jd = swe.julday(now.year, now.month, now.day,
                    now.hour - timezone + now.minute/60)

    sun = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
    moon = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]

    angle = (moon - sun) % 360

    # -------- TITHI --------
    tithi_index = floor(angle / 12)
    tithi = TITHIS[tithi_index]
    tithi_progress = int((angle % 12) / 12 * 100)

    next_tithi_angle = (tithi_index + 1) * 12
    tithi_end_jd = calculate_end_time(
        jd,
        next_tithi_angle,
        lambda x: (swe.calc_ut(x, swe.MOON)[0][0] -
                   swe.calc_ut(x, swe.SUN)[0][0]) % 360
    )

    # -------- NAKSHATRA --------
    nak_index = floor(moon / (360/27))
    nakshatra = NAKSHATRAS[nak_index]

    next_nak_angle = (nak_index + 1) * (360/27)
    nak_end_jd = calculate_end_time(
        jd,
        next_nak_angle,
        lambda x: swe.calc_ut(x, swe.MOON)[0][0]
    )

    # -------- YOGA --------
    yoga_angle = (sun + moon) % 360
    yoga_index = floor(yoga_angle / (360/27))
    yoga = YOGAS[yoga_index]

    next_yoga_angle = (yoga_index + 1) * (360/27)
    yoga_end_jd = calculate_end_time(
        jd,
        next_yoga_angle,
        lambda x: (swe.calc_ut(x, swe.SUN)[0][0] +
                   swe.calc_ut(x, swe.MOON)[0][0]) % 360
    )

    # -------- KARANA --------
    karana_index = floor(angle / 6) % 7
    karana = KARANAS[karana_index]

    next_karana_angle = (floor(angle / 6) + 1) * 6
    karana_end_jd = calculate_end_time(
        jd,
        next_karana_angle,
        lambda x: (swe.calc_ut(x, swe.MOON)[0][0] -
                   swe.calc_ut(x, swe.SUN)[0][0]) % 360
    )

    # -------- SUNRISE / SUNSET --------
    sunrise_jd, sunset_jd = get_sun_times(jd, lat, lon)

    day_length = sunset_jd - sunrise_jd
    segment = day_length / 8

    weekday = now.weekday()

    rahu_map = [7,1,6,4,5,3,2]
    yama_map = [4,3,2,1,7,6,5]
    gulika_map = [6,5,4,3,2,1,7]

    def segment_time(index):
        start = sunrise_jd + segment*(index-1)
        end = start + segment
        return f"{format_time(start)} - {format_time(end)}"

    rahu = segment_time(rahu_map[weekday])
    yamaganda = segment_time(yama_map[weekday])
    gulika = segment_time(gulika_map[weekday])

    # -------- ABHIJIT --------
    midday = sunrise_jd + day_length/2
    abhijit = f"{format_time(midday-0.02)} - {format_time(midday+0.02)}"

    # -------- BRAHMA MUHURTA --------
    brahma = f"{format_time(sunrise_jd-0.06)} - {format_time(sunrise_jd-0.03)}"

    # -------- MOON PHASE --------
    phase_percent = int((angle / 360) * 100)
    if phase_percent < 25:
        phase = "🌑 New Moon"
    elif phase_percent < 50:
        phase = "🌓 First Quarter"
    elif phase_percent < 75:
        phase = "🌕 Full Moon"
    else:
        phase = "🌗 Last Quarter"

    # -------- PLANETS --------
    planets_list = []
    planet_ids = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mercury": swe.MERCURY,
        "Venus": swe.VENUS,
        "Mars": swe.MARS,
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN
    }

    for name, pid in planet_ids.items():
        pos = swe.calc_ut(jd, pid)[0][0]
        sign_index = floor(pos / 30)
        degree = pos % 30
        nak = NAKSHATRAS[floor(pos/(360/27))]
        planets_list.append({
            "name": name,
            "sign": sign_index,
            "degree": f"{degree:.2f}°",
            "nakshatra": nak
        })

    return {
        "date": now.strftime("%A, %B %d, %Y"),
        "moon_phase": phase,
        "tithi": tithi,
        "tithi_progress": tithi_progress,
        "tithi_end": format_time(tithi_end_jd),
        "nakshatra": nakshatra,
        "nakshatra_end": format_time(nak_end_jd),
        "yoga": yoga,
        "yoga_end": format_time(yoga_end_jd),
        "karana": karana,
        "karana_end": format_time(karana_end_jd),
        "sunrise": format_time(sunrise_jd),
        "sunset": format_time(sunset_jd),
        "rahu": rahu,
        "yamaganda": yamaganda,
        "gulika": gulika,
        "abhijit": abhijit,
        "brahma": brahma,
        "planets": planets_list
    }

    '''
# -------------------------------------------------------- end  ----------------------

'''
import swisseph as swe
from datetime import datetime

# ===============================
# INITIAL SETUP
# ===============================

swe.set_ephe_path('.')  
swe.set_sid_mode(swe.SIDM_LAHIRI)

IST_OFFSET = 5.5
NAK_DIV = 13.3333333333


# ===============================
# CITY COORDINATES
# ===============================

CITIES = {
    "Pune": (18.5204, 73.8567),
    "Ujjain": (23.1765, 75.7885),
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
}


# ===============================
# UTILITY FUNCTIONS
# ===============================

def to_dms(deg):
    d = int(deg)
    m = int((deg - d) * 60)
    return f"{d}°{m:02d}'"

TITHI_NAMES = [
"Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami",
"Shashthi","Saptami","Ashtami","Navami","Dashami",
"Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Purnima",
"Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami",
"Shashthi","Saptami","Ashtami","Navami","Dashami",
"Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Amavasya"
]

NAKSHATRA_NAMES = [
"Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
"Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
"Uttara Phalguni","Hasta","Chitra","Swati","Vishakha",
"Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha",
"Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
"Uttara Bhadrapada","Revati"
]

RASHI_NAMES = [
"Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya",
"Tula","Vrischika","Dhanu","Makara","Kumbha","Meena"
]

KARANA_NAMES = [
"Bava","Balava","Kaulava","Taitila","Garaja",
"Vanija","Vishti"
]
def jd_to_ist(jd):
    y, m, d, hour = swe.revjul(jd)
    hour += IST_OFFSET

    if hour >= 24:
        hour -= 24

    h = int(hour)
    minute = int((hour - h) * 60)

    return f"{h:02d}:{minute:02d}"


def get_sun_times(jd, lat, lon):

    geopos = (lon, lat, 0.0)

    sunrise = swe.rise_trans(
        jd,
        swe.SUN,
        swe.CALC_RISE | swe.BIT_DISC_CENTER,
        geopos,
        1013.25,
        15
    )[1][0]

    sunset = swe.rise_trans(
        jd,
        swe.SUN,
        swe.CALC_SET | swe.BIT_DISC_CENTER,
        geopos,
        1013.25,
        15
    )[1][0]

    return sunrise, sunset


# ===============================
# CORE PANCHANG ENGINE
# ===============================

def get_full_panchang(city):

    if city not in CITIES:
        return {"error": "City not supported"}

    lat, lon = CITIES[city]

    now = datetime.now()

    year = now.year
    month = now.month
    day = now.day
    hour = now.hour + now.minute / 60

    # Convert IST → UTC for JD
    jd = swe.julday(year, month, day, hour - IST_OFFSET)

    # ===============================
    # PLANET LONGITUDES (SIDEREAL)
    # ===============================

    sun = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
    moon = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]

    diff = (moon - sun) % 360

    # ===============================
    # TITHI
    # ===============================

    tithi_number = int(diff / 12) + 1

    # ===============================
    # NAKSHATRA
    # ===============================

    nak_number = int(moon / NAK_DIV) + 1

    # ===============================
    # YOGA
    # ===============================

    yoga_long = (sun + moon) % 360
    yoga_number = int(yoga_long / NAK_DIV) + 1

    # ===============================
    # KARANA
    # ===============================

    karana_number = int(diff / 6) + 1

    # ===============================
    # SUNRISE / SUNSET
    # ===============================

    sunrise_jd, sunset_jd = get_sun_times(jd, lat, lon)

    sunrise = jd_to_ist(sunrise_jd)
    sunset = jd_to_ist(sunset_jd)

    # ===============================
    # RAHU KAAL
    # ===============================

    day_length = sunset_jd - sunrise_jd
    segment = day_length / 8

    weekday_index = now.weekday()
    rahu_map = [7,1,6,4,5,3,2]  # Mon-Sun

    rahu_start = sunrise_jd + segment * rahu_map[weekday_index]
    rahu_end = rahu_start + segment

    rahu_start_time = jd_to_ist(rahu_start)
    rahu_end_time = jd_to_ist(rahu_end)

    # ===============================
    # MOON PHASE %
    # ===============================

    moon_phase = round((diff / 360) * 100, 2)

    # ===============================
    # PLANET TABLE
    # ===============================

    planet_list = [
        ("Sun", swe.SUN),
        ("Moon", swe.MOON),
        ("Mercury", swe.MERCURY),
        ("Venus", swe.VENUS),
        ("Mars", swe.MARS),
        ("Jupiter", swe.JUPITER),
        ("Saturn", swe.SATURN),
    ]

    planets = []

    for name, p in planet_list:
        data = swe.calc_ut(jd, p, swe.FLG_SIDEREAL | swe.FLG_SPEED)
        lon = data[0][0]
        speed = data[0][3]

        planets.append({
            "planet": name,
            "degree": to_dms(lon % 30),
            "sign_index": int(lon / 30) + 1,
            "retrograde": speed < 0
        })

    # ===============================
    # FINAL STRUCTURED RESPONSE
    # ===============================

    return {
        "city": city,
        "date": now.strftime("%A, %B %d, %Y"),
        "moon_phase_percent": moon_phase,

        "panchang": {
            "tithi_number": tithi_number,
            "nakshatra_number": nak_number,
            "yoga_number": yoga_number,
            "karana_number": karana_number,
        },

        "sun_times": {
            "sunrise": sunrise,
            "sunset": sunset,
        },

        "rahu_kaal": {
            "start": rahu_start_time,
            "end": rahu_end_time
        },

        "planets": planets
    }


    '''
import swisseph as swe
#from datetime import datetime, timedelta
from datetime import datetime, timezone


# ==============================
# BASIC SETTINGS
# ==============================

swe.set_ephe_path('.')
swe.set_sid_mode(swe.SIDM_LAHIRI)

IST_OFFSET = 5.5
NAK_DIV = 13.3333333333

# ==============================
# CITY DATABASE
# ==============================

CITIES = {
    "Pune": (18.5204, 73.8567),
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.6139, 77.2090),
    "Bangalore": (12.9716, 77.5946),
}

# ==============================
# NAME ARRAYS
# ==============================

TITHI_NAMES = [
"Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami",
"Shashthi","Saptami","Ashtami","Navami","Dashami",
"Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Purnima",
"Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami",
"Shashthi","Saptami","Ashtami","Navami","Dashami",
"Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Amavasya"
]

NAKSHATRA_NAMES = [
"Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
"Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
"Uttara Phalguni","Hasta","Chitra","Swati","Vishakha",
"Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha",
"Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
"Uttara Bhadrapada","Revati"
]

RASHI_NAMES = [
"Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya",
"Tula","Vrischika","Dhanu","Makara","Kumbha","Meena"
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

# ==============================
# UTILITIES
# ==============================

def jd_to_ist(jd):
    y, m, d, hour = swe.revjul(jd)
    hour += IST_OFFSET
    if hour >= 24:
        hour -= 24
    h = int(hour)
    minute = int((hour - h) * 60)
    return f"{h:02d}:{minute:02d}"

def get_sun_times(jd, lat, lon):
    geopos = (lon, lat, 0)
    sunrise = swe.rise_trans(jd, swe.SUN,
                             swe.CALC_RISE | swe.BIT_DISC_CENTER,
                             geopos, 1013.25, 15)[1][0]
    sunset = swe.rise_trans(jd, swe.SUN,
                            swe.CALC_SET | swe.BIT_DISC_CENTER,
                            geopos, 1013.25, 15)[1][0]
    return sunrise, sunset

# ==============================
# CORE ENGINE
# ==============================

def get_full_panchang(city):

    if city not in CITIES:
        return {"error": "City not supported"}

    lat, lon = CITIES[city]

    now = datetime.now()
    #jd = swe.julday(now.year, now.month, now.day,
    #                now.hour + now.minute/60 - IST_OFFSET)

    now = datetime.now(timezone.utc)

    jd = swe.julday(
        now.year,
        now.month,
        now.day,
        now.hour + now.minute/60 + now.second/3600
    )

    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    sun = swe.calc_ut(jd, swe.SUN, FLAGS)[0][0]
    moon = swe.calc_ut(jd, swe.MOON, FLAGS)[0][0]

    #sun = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
    #moon = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]

    diff = (moon - sun) % 360

    # ---------------- TITHI ----------------
    tithi_no = int(diff / 12) + 1
    paksha = "Shukla" if tithi_no <= 15 else "Krishna"
    tithi_name = TITHI_NAMES[tithi_no - 1]

    # ---------------- NAKSHATRA ----------------
    nak_no = int(moon / NAK_DIV) + 1
    #nak_name = NAKSHATRA_NAMES[nak_no - 1]
    nak_name = NAKSHATRA_NAMES[(nak_no - 1) % 27]

    # ---------------- YOGA ----------------
    yoga_no = int(((sun + moon) % 360) / NAK_DIV) + 1
    yoga_name = YOGA_NAMES[yoga_no - 1]

    # ---------------- KARANA ----------------
    karana_no = int(diff / 6) + 1
    karana_name = KARANA_NAMES[(karana_no - 1) % 7]

    # ---------------- SUN TIMES ----------------
    jd_day_start = swe.julday(now.year, now.month, now.day, 0)
    sunrise_jd, sunset_jd = get_sun_times(jd, lat, lon)
    sunrise = jd_to_ist(sunrise_jd)
    sunset = jd_to_ist(sunset_jd)

    # ---------------- RAHU / YAMAGANDA / GULIKA ----------------
    day_length = sunset_jd - sunrise_jd
    segment = day_length / 8

    weekday = now.weekday()

    rahu_map = [7,1,6,4,5,3,2]
    yam_map  = [4,3,2,1,0,6,5]
    gulika_map = [6,5,4,3,2,1,0]

    rahu = jd_to_ist(sunrise_jd + segment * rahu_map[weekday]) + \
           " - " + jd_to_ist(sunrise_jd + segment * (rahu_map[weekday]+1))

    yamaganda = jd_to_ist(sunrise_jd + segment * yam_map[weekday]) + \
                " - " + jd_to_ist(sunrise_jd + segment * (yam_map[weekday]+1))

    gulika = jd_to_ist(sunrise_jd + segment * gulika_map[weekday]) + \
             " - " + jd_to_ist(sunrise_jd + segment * (gulika_map[weekday]+1))

    # ---------------- ABHIJIT ----------------
    mid = sunrise_jd + day_length/2
    abhijit = jd_to_ist(mid - (24/1440)) + " - " + jd_to_ist(mid + (24/1440))

    # ---------------- BRAHMA ----------------
    brahma_start = sunrise_jd - (96/1440)
    brahma_end = sunrise_jd - (48/1440)
    brahma = jd_to_ist(brahma_start) + " - " + jd_to_ist(brahma_end)

    # ---------------- MOON PHASE ----------------
    moon_phase_percent = round((diff / 360) * 100, 2)
    waxing = "Waxing" if diff < 180 else "Waning"

    # ---------------- PLANETS ----------------
    planet_list = [
        ("Sun", swe.SUN),
        ("Moon", swe.MOON),
        ("Mercury", swe.MERCURY),
        ("Venus", swe.VENUS),
        ("Mars", swe.MARS),
        ("Jupiter", swe.JUPITER),
        ("Saturn", swe.SATURN),
    ]

    planets = []

    for name, p in planet_list:
        data = swe.calc_ut(jd, p, swe.FLG_SIDEREAL | swe.FLG_SPEED)
        lon = data[0][0]
        speed = data[0][3]

        sign_index = int(lon / 30)
        sign_name = RASHI_NAMES[sign_index]

        planets.append({
            "name": name,
            "sign": sign_name,
            "degree": f"{int(lon%30)}°{int((lon%1)*60):02d}'",
            "nakshatra": NAKSHATRA_NAMES[int(lon / NAK_DIV)],
            "retrograde": speed < 0
        })

    # ==============================
    # FINAL RESPONSE
    # ==============================

    return {
        "date": now.strftime("%A, %B %d, %Y"),
        "moon_phase": f"{waxing} {moon_phase_percent}%",
        "tithi": f"{tithi_name} ({paksha})",
        "tithi_progress": moon_phase_percent,
        "tithi_end": "",
        "nakshatra": nak_name,
        "nakshatra_end": "",
        "yoga": yoga_name,
        "yoga_end": "",
        "karana": karana_name,
        "karana_end": "",
        "sunrise": sunrise,
        "sunset": sunset,
        "rahu": rahu,
        "yamaganda": yamaganda,
        "gulika": gulika,
        "abhijit": abhijit,
        "brahma": brahma,
        "planets": planets
    }