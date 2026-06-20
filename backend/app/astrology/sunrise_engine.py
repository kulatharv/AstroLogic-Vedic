import swisseph as swe

def calculate_sun_times(jd, lat, lon):

    # Sunrise
    sunrise = swe.rise_trans(
        jd, swe.SUN,
        lon, lat,
        rsmi=swe.CALC_RISE
    )[1][0]

    # Sunset
    sunset = swe.rise_trans(
        jd, swe.SUN,
        lon, lat,
        rsmi=swe.CALC_SET
    )[1][0]

    return sunrise, sunset