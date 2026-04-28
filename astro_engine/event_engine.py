# astro_engine/event_engine.py


def evaluate_event(chart, event_type):

    score = 0
    confidence = 0.5
    reasons = []

    planets_by_house = chart.get("planets_by_house", {})
    house_lords = chart.get("house_lords", {})
    strengths = chart.get("planet_strength_scores", {})
    functional = chart.get("functional_nature", {})
    yogas = chart.get("advanced_yogas", [])
    activated = chart.get("activated_houses", [])
    transits = chart.get("current_transits", {})
    aspects = chart.get("vedic_aspects", {})

    # Reverse mapping: planet → house
    planet_house = {}
    for house, plist in planets_by_house.items():
        for p in plist:
            planet_house[p["planet"]] = house

    # -------------------------------
    # MARRIAGE EVENT LOGIC
    # -------------------------------
    if event_type == "marriage":

        # Relevant houses
        relevant_houses = [7, 2, 11, 5]

        # 1️⃣ Natal Promise Check
        for house in relevant_houses:
            if house in planets_by_house:
                score += 5
                reasons.append(f"Planets influencing house {house}")

        # 2️⃣ 7th Lord Strength
        seventh_lord = house_lords[7]["lord"]
        lord_strength = strengths.get(seventh_lord, 0.5)

        score += lord_strength * 25
        reasons.append(f"7th lord strength: {lord_strength}")

        # 3️⃣ Venus strength (general marriage karaka)
        venus_strength = strengths.get("Venus", 0.5)
        score += venus_strength * 15
        reasons.append(f"Venus strength: {venus_strength}")

        # 4️⃣ Dasha Activation
        if 7 in activated:
            score += 20
            reasons.append("7th house activated by dasha")

        # 5️⃣ Transit Trigger
        if transits.get("Jupiter", {}).get("house_from_lagna") == 7:
            score += 15
            reasons.append("Jupiter transiting 7th house")

        # 6️⃣ Yogas Influence
        if "Raj Yoga" in yogas:
            score += 5
            reasons.append("Raj Yoga supports life stability")

        if "Vipreet Raj Yoga" in yogas:
            score += 3
            reasons.append("Vipreet Raj Yoga gives unexpected gains")

    # -------------------------------
    # CAREER EVENT LOGIC
    # -------------------------------
    elif event_type == "career":

        relevant_houses = [10, 6, 2]

        for house in relevant_houses:
            if house in planets_by_house:
                score += 5
                reasons.append(f"Planets influencing house {house}")

        tenth_lord = house_lords[10]["lord"]
        lord_strength = strengths.get(tenth_lord, 0.5)

        score += lord_strength * 25
        reasons.append(f"10th lord strength: {lord_strength}")

        saturn_strength = strengths.get("Saturn", 0.5)
        score += saturn_strength * 15
        reasons.append(f"Saturn strength: {saturn_strength}")

        if 10 in activated:
            score += 20
            reasons.append("10th house activated by dasha")

        if transits.get("Jupiter", {}).get("house_from_lagna") == 10:
            score += 15
            reasons.append("Jupiter transiting 10th house")

        if "Raj Yoga" in yogas:
            score += 10
            reasons.append("Raj Yoga supports authority")

    else:
        return {
            "error": "Event type not supported"
        }

    # -------------------------------
    # Normalize Score
    # -------------------------------
    score = min(100, round(score, 2))

    # Confidence based on strength coverage
    confidence += (score / 200)
    confidence = min(1.0, round(confidence, 2))

    # Interpretation level
    if score >= 75:
        level = "Very Strong"
    elif score >= 55:
        level = "Strong"
    elif score >= 35:
        level = "Moderate"
    else:
        level = "Weak / Delayed"

    return {
        "event": event_type,
        "score": score,
        "confidence": confidence,
        "level": level,
        "reasons": reasons
    }
