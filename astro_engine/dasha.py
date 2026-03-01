from astro_engine.nakshatra import NAKSHATRAS
from datetime import timedelta

DASHA_SEQUENCE = [
    "Ketu", "Venus", "Sun", "Moon",
    "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

DASHA_YEARS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17
}

NAKSHATRA_SIZE = 13 + (20/60)


def get_nakshatra_lord(nak_name):

    nak_index = NAKSHATRAS.index(nak_name)
    lord = DASHA_SEQUENCE[nak_index % 9]
    return lord


def calculate_mahadasha(moon_longitude, nak_name):

    lord = get_nakshatra_lord(nak_name)

    full_years = DASHA_YEARS[lord]

    remainder = moon_longitude % NAKSHATRA_SIZE
    balance_fraction = (NAKSHATRA_SIZE - remainder) / NAKSHATRA_SIZE

    balance_years = balance_fraction * full_years

    return lord, round(balance_years, 2)
def generate_dasha_timeline(start_lord, balance_years):

    timeline = []

    current_index = DASHA_SEQUENCE.index(start_lord)

    # First partial period
    timeline.append({
        "lord": start_lord,
        "years": round(balance_years, 2)
    })

    total_years = balance_years

    # Continue full cycle
    next_index = (current_index + 1) % 9

    while total_years < 120:

        lord = DASHA_SEQUENCE[next_index]
        years = DASHA_YEARS[lord]

        timeline.append({
            "lord": lord,
            "years": years
        })

        total_years += years
        next_index = (next_index + 1) % 9

    return timeline


def generate_antardasha(mahadasha_lord):

    antardasha_list = []

    start_index = DASHA_SEQUENCE.index(mahadasha_lord)

    mahadasha_years = DASHA_YEARS[mahadasha_lord]

    for i in range(9):

        lord = DASHA_SEQUENCE[(start_index + i) % 9]

        years = (mahadasha_years * DASHA_YEARS[lord]) / 120

        antardasha_list.append({
            "lord": lord,
            "years": round(years, 2)
        })

    return antardasha_list
def generate_dasha_calendar(birth_datetime, timeline):

    calendar = []

    current_date = birth_datetime

    for period in timeline:

        duration_days = period["years"] * 365.25

        end_date = current_date + timedelta(days=duration_days)

        calendar.append({
            "lord": period["lord"],
            "start": current_date,
            "end": end_date
        })

        current_date = end_date

    return calendar

def generate_pratyantardasha(mahadasha_lord, antardasha_lord):

    pratyantardasha_list = []

    start_index = DASHA_SEQUENCE.index(antardasha_lord)

    mahadasha_years = DASHA_YEARS[mahadasha_lord]
    antardasha_years = (mahadasha_years * DASHA_YEARS[antardasha_lord]) / 120

    for i in range(9):

        lord = DASHA_SEQUENCE[(start_index + i) % 9]

        years = (antardasha_years * DASHA_YEARS[lord]) / 120

        pratyantardasha_list.append({
            "lord": lord,
            "years": round(years, 3)
        })

    return pratyantardasha_list
