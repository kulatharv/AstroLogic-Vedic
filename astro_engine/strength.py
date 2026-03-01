EXALTATION = {
    "Sun": "Aries",
    "Moon": "Taurus",
    "Mars": "Capricorn",
    "Mercury": "Virgo",
    "Jupiter": "Cancer",
    "Venus": "Pisces",
    "Saturn": "Libra",
    "Rahu": "Taurus",
    "Ketu": "Scorpio"
}

DEBILITATION = {
    "Sun": "Libra",
    "Moon": "Scorpio",
    "Mars": "Cancer",
    "Mercury": "Pisces",
    "Jupiter": "Capricorn",
    "Venus": "Virgo",
    "Saturn": "Aries",
    "Rahu": "Scorpio",
    "Ketu": "Taurus"
}

OWN_SIGNS = {
    "Sun": ["Leo"],
    "Moon": ["Cancer"],
    "Mars": ["Aries", "Scorpio"],
    "Mercury": ["Gemini", "Virgo"],
    "Jupiter": ["Sagittarius", "Pisces"],
    "Venus": ["Taurus", "Libra"],
    "Saturn": ["Capricorn", "Aquarius"]
}
def evaluate_strength(planet, sign):

    if planet in EXALTATION and EXALTATION[planet] == sign:
        return "Exalted 🔥"

    if planet in DEBILITATION and DEBILITATION[planet] == sign:
        return "Debilitated ❌"

    if planet in OWN_SIGNS and sign in OWN_SIGNS[planet]:
        return "Own Sign 💪"

    return "Normal"
def final_strength(planet, rasi_sign, navamsa_sign):

    base = evaluate_strength(planet, rasi_sign)

    nav_strength = evaluate_strength(planet, navamsa_sign)

    if base == "Debilitated ❌" and nav_strength != "Debilitated ❌":
        return "Improved via Navamsa ⭐"

    if base == "Normal" and nav_strength in ["Exalted 🔥", "Own Sign 💪"]:
        return "Strengthened in D9 💎"

    return base
