EXALTATION = {
    "Sun": "Aries",
    "Moon": "Taurus",
    "Mars": "Capricorn",
    "Mercury": "Virgo",
    "Jupiter": "Cancer",
    "Venus": "Pisces",
    "Saturn": "Libra"
}

DEBILITATION = {
    "Sun": "Libra",
    "Moon": "Scorpio",
    "Mars": "Cancer",
    "Mercury": "Pisces",
    "Jupiter": "Capricorn",
    "Venus": "Virgo",
    "Saturn": "Aries"
}


def calculate_weighted_strength(chart):

    planets = chart["planets_by_house"]
    functional = chart.get("functional_nature", {})

    strength_scores = {}

    for house, plist in planets.items():
        for p in plist:

            planet = p["planet"]
            sign = p["sign"]
            navamsa = p["navamsa"]

            score = 0.5  # base

            # Exaltation
            if EXALTATION.get(planet) == sign:
                score += 0.3

            # Debilitation
            if DEBILITATION.get(planet) == sign:
                score -= 0.3

            # Navamsa support
            if EXALTATION.get(planet) == navamsa:
                score += 0.1

            # Functional benefic boost
            if functional.get(planet) == "Functional Benefic":
                score += 0.05

            # Functional malefic reduction
            if functional.get(planet) == "Functional Malefic":
                score -= 0.05

            # Bound between 0 and 1
            score = max(0, min(1, score))

            strength_scores[planet] = round(score, 2)

    return strength_scores
