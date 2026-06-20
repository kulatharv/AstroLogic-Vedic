SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def degree_to_sign(degree):
    sign_index = int(degree // 30)
    sign_degree = degree % 30
    return SIGNS[sign_index], round(sign_degree, 2)
