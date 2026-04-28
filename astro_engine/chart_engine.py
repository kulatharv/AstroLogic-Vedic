import swisseph as swe
from collections import defaultdict
from datetime import datetime

from astro_engine.planets import calculate_all_planets
from astro_engine.zodiac import degree_to_sign
from astro_engine.houses import calculate_lagna, assign_house, assign_bhava_house
from astro_engine.nakshatra import calculate_nakshatra
from astro_engine.navamsa import calculate_navamsa
from astro_engine.strength import final_strength
from astro_engine.dasha import calculate_mahadasha, generate_dasha_timeline
from astro_engine.house_lords import calculate_house_lords
from astro_engine.dasha_activation import activated_houses
from astro_engine.functional_nature import classify_functional_nature
from astro_engine.dispositor import calculate_dispositors
from astro_engine.vedic_aspects import calculate_vedic_aspects
from astro_engine.transits import calculate_transits
from astro_engine.timing_engine import evaluate_event_trigger
from astro_engine.yogas_engine import detect_advanced_yogas
from astro_engine.weighted_strength import calculate_weighted_strength
from astro_engine.event_engine import evaluate_event
from astro_engine.explanation_builder import build_event_explanation




def generate_full_chart(year, month, day, hour, latitude, longitude):

    # ---------------------------
    # TIMEZONE (IST → UTC)
    # ---------------------------
    timezone_offset = 5.5
    utc_hour = hour - timezone_offset

    if utc_hour < 0:
        utc_hour += 24
        day -= 1

    jd = swe.julday(year, month, day, utc_hour)

    # ---------------------------
    # PLANET CALCULATIONS
    # ---------------------------
    planet_positions = calculate_all_planets(jd)

    # ---------------------------
    # LAGNA
    # ---------------------------
    asc_degree, lagna_sign = calculate_lagna(jd, latitude, longitude)

    # ---------------------------
    # HOUSE LORDS
    # ---------------------------
    house_lords = calculate_house_lords(lagna_sign)

    functional_nature = classify_functional_nature(lagna_sign, house_lords)


    # ---------------------------
    # GROUP PLANETS BY HOUSE
    # ---------------------------
    house_data = defaultdict(list)

    for planet, degree in planet_positions.items():

        sign, sign_degree = degree_to_sign(degree)
        navamsa_sign = calculate_navamsa(degree)
        strength = final_strength(planet, sign, navamsa_sign)

        rasi_house = assign_house(sign, lagna_sign)
        bhava_house = assign_bhava_house(jd, latitude, longitude, degree)

        nak, pada = calculate_nakshatra(degree)

        house_data[rasi_house].append({
            "planet": planet,
            "degree": round(sign_degree, 2),
            "sign": sign,
            "navamsa": navamsa_sign,
            "nakshatra": nak,
            "pada": pada,
            "bhava_house": bhava_house,
            "strength": strength
        })

    # Convert defaultdict to normal dict
    planets_by_house = dict(house_data)

    # ---------------------------
    # DASHA
    # ---------------------------
    moon_longitude = planet_positions["Moon"]
    moon_nak, _ = calculate_nakshatra(moon_longitude)

    dasha_lord, balance = calculate_mahadasha(moon_longitude, moon_nak)
    timeline = generate_dasha_timeline(dasha_lord, balance)

   # ---------------------------
    # BUILD CHART OBJECT
    # ---------------------------

    chart = {
        "basic_details": {
            "date": f"{day}-{month}-{year}",
            "time": hour,
            "lagna": lagna_sign
        },
        "planets_by_house": planets_by_house,
        "house_lords": house_lords,
        "dasha": {
            "current_mahadasha": dasha_lord,
            "balance_years": round(balance, 2),
            "timeline": timeline
        }
    }

    # ---------------------------
    # ADD ACTIVATION
    # ---------------------------

    chart["activated_houses"] = activated_houses(chart)

    # ---------------------------
    # ADD FUNCTIONAL NATURE
    # ---------------------------

    chart["functional_nature"] = classify_functional_nature(lagna_sign, house_lords)

    # ---------------------------
    # ADD DISPOSITORS
    # ---------------------------

    chart["dispositors"] = calculate_dispositors(chart)
    chart["vedic_aspects"] = calculate_vedic_aspects(chart)
    from datetime import datetime

    today = datetime.today()

    chart["current_transits"] = calculate_transits(
        chart,
        today.year,
        today.month,
        today.day
    )


    chart["marriage_timing"] = evaluate_event_trigger(chart, "marriage")
    chart["career_timing"] = evaluate_event_trigger(chart, "career")
    chart["advanced_yogas"] = detect_advanced_yogas(chart)
    chart["planet_strength_scores"] = calculate_weighted_strength(chart)
    chart["marriage_prediction"] = evaluate_event(chart, "marriage")
    chart["career_prediction"] = evaluate_event(chart, "career")
    chart["marriage_explanation"] = build_event_explanation(chart, "marriage")
    chart["career_explanation"] = build_event_explanation(chart, "career")

    return chart
