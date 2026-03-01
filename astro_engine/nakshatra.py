NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika",
    "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

NAKSHATRA_SIZE = 13 + (20/60)   # 13°20'
PADA_SIZE = NAKSHATRA_SIZE / 4


def calculate_nakshatra(longitude):

    nak_index = int(longitude / NAKSHATRA_SIZE)
    nak_name = NAKSHATRAS[nak_index]

    remainder = longitude % NAKSHATRA_SIZE
    pada = int(remainder / PADA_SIZE) + 1

    return nak_name, pada
