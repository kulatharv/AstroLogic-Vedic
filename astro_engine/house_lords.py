from astro_engine.zodiac import SIGNS

SIGN_LORDS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter"
}


def calculate_house_lords(lagna_sign):

    lagna_index = SIGNS.index(lagna_sign)

    house_lords = {}

    for house in range(1, 13):

        sign_index = (lagna_index + house - 1) % 12
        sign = SIGNS[sign_index]
        lord = SIGN_LORDS[sign]

        house_lords[house] = {
            "sign": sign,
            "lord": lord
        }

    return house_lords
