import swisseph as swe
from astro_engine.zodiac import degree_to_sign, SIGNS


def calculate_lagna(jd, latitude, longitude):

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SIDEREAL

    cusps, ascmc = swe.houses_ex(
        jd,
        latitude,
        longitude,
        b'W',
        flags
    )

    asc_degree = ascmc[0]
    sign, _ = degree_to_sign(asc_degree)

    return asc_degree, sign


def assign_house(planet_sign, lagna_sign):

    lagna_index = SIGNS.index(lagna_sign)
    planet_index = SIGNS.index(planet_sign)

    house_number = (planet_index - lagna_index) % 12 + 1

    return house_number


def assign_bhava_house(jd, latitude, longitude, planet_longitude):

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SIDEREAL

    cusps, ascmc = swe.houses_ex(
        jd,
        latitude,
        longitude,
        b'P',
        flags
    )

    cusp_list = list(cusps)

    # Remove first dummy value if present
    if len(cusp_list) == 13:
        cusp_list = cusp_list[1:]

    if len(cusp_list) != 12:
        # fallback safety
        return None

    for i in range(12):

        start = cusp_list[i]

        if i < 11:
            end = cusp_list[i + 1]
        else:
            end = cusp_list[0] + 360  # wrap-around

        pl = planet_longitude

        if pl < start:
            pl += 360

        if start <= pl < end:
            return i + 1

    return None
