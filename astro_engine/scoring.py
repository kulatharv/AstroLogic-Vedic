def calculate_chart_scores(chart_data):

    scores = {
        "overall_strength": 0,
        "marriage_score": 0,
        "career_score": 0,
        "finance_score": 0,
        "mental_score": 0
    }

    house_data = chart_data.get("planets_by_house", {})

    # ---------- OVERALL STRENGTH ----------
    for house, planets in house_data.items():
        for p in planets:
            if "Exalted" in p["strength"]:
                scores["overall_strength"] += 10
            elif "Own Sign" in p["strength"]:
                scores["overall_strength"] += 8
            elif "Improved" in p["strength"]:
                scores["overall_strength"] += 6
            elif "Debilitated" in p["strength"]:
                scores["overall_strength"] -= 5

    # ---------- MARRIAGE SCORE ----------
    if 7 in house_data:
        scores["marriage_score"] += 15

        for p in house_data[7]:
            if p["planet"] in ["Venus", "Jupiter"]:
                scores["marriage_score"] += 10

    # ---------- CAREER SCORE ----------
    if 10 in house_data:
        scores["career_score"] += 15

        for p in house_data[10]:
            if p["planet"] in ["Sun", "Saturn"]:
                scores["career_score"] += 10

    # ---------- FINANCE SCORE ----------
    for house in [2, 11]:
        if house in house_data:
            scores["finance_score"] += 10

    # ---------- MENTAL SCORE ----------
    for house, planets in house_data.items():
        for p in planets:
            if p["planet"] == "Moon":
                if "Debilitated" in p["strength"]:
                    scores["mental_score"] -= 10
                else:
                    scores["mental_score"] += 10



    return scores
