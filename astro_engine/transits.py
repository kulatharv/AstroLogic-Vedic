import swisseph as swe
from astro_engine.zodiac import degree_to_sign
from astro_engine.houses import assign_house


def calculate_transits(chart, current_year, current_month, current_day):

    lagna = chart["basic_details"]["lagna"]

    jd = swe.julday(current_year, current_month, current_day, 0)

    planets = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE
    }

    transit_data = {}

    for name, code in planets.items():

        position = swe.calc_ut(jd, code)[0][0]
        sign, _ = degree_to_sign(position)

        house = assign_house(sign, lagna)

        transit_data[name] = {
            "sign": sign,
            "house_from_lagna": house
        }

    return transit_data
