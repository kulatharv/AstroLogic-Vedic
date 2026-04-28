from astro_engine.zodiac import SIGNS, degree_to_sign

MOVABLE = ["Aries", "Cancer", "Libra", "Capricorn"]
FIXED = ["Taurus", "Leo", "Scorpio", "Aquarius"]
DUAL = ["Gemini", "Virgo", "Sagittarius", "Pisces"]

NAVAMSA_SIZE = 30 / 9  # 3.3333°


def calculate_navamsa(longitude):

    sign, sign_degree = degree_to_sign(longitude)
    sign_index = SIGNS.index(sign)

    nav_number = int(sign_degree / NAVAMSA_SIZE)

    if sign in MOVABLE:
        start_index = sign_index

    elif sign in FIXED:
        start_index = (sign_index + 8) % 12  # 9th from it

    else:  # DUAL
        start_index = (sign_index + 4) % 12  # 5th from it

    navamsa_sign_index = (start_index + nav_number) % 12
    navamsa_sign = SIGNS[navamsa_sign_index]

    return navamsa_sign
