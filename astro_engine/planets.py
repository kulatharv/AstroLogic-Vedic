

import swisseph as swe

def calculate_all_planets(jd):

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SIDEREAL

    planets = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": swe.TRUE_NODE,
        "Ketu": swe.TRUE_NODE
    }

    positions = {}

    for name, code in planets.items():
        result = swe.calc_ut(jd, code, flags)
        longitude = result[0][0]

        if name == "Ketu":
            longitude = (longitude + 180) % 360

        positions[name] = longitude

    return positions
