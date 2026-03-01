def evaluate_event_trigger(chart, event_type):

    activated = chart["activated_houses"]
    transits = chart.get("current_transits", {})
    aspects = chart.get("vedic_aspects", {})

    trigger_score = 0
    reasons = []

    # --------------------
    # Marriage Timing Logic
    # --------------------
    if event_type == "marriage":

        # Dasha activation
        if 7 in activated:
            trigger_score += 30
            reasons.append("7th house activated by dasha")

        # Jupiter transit over 7th house
        if transits.get("Jupiter", {}).get("house_from_lagna") == 7:
            trigger_score += 30
            reasons.append("Jupiter transiting 7th house")

        # Saturn not afflicting 7th
        if transits.get("Saturn", {}).get("house_from_lagna") != 7:
            trigger_score += 10
            reasons.append("Saturn not afflicting 7th house")

        # Venus aspecting 7th
        if 7 in aspects.get("Venus", []):
            trigger_score += 15
            reasons.append("Venus aspecting 7th house")

    # --------------------
    # Career Timing Logic
    # --------------------
    if event_type == "career":

        if 10 in activated:
            trigger_score += 30
            reasons.append("10th house activated by dasha")

        if transits.get("Jupiter", {}).get("house_from_lagna") == 10:
            trigger_score += 25
            reasons.append("Jupiter transiting 10th house")

        if 10 in aspects.get("Saturn", []):
            trigger_score += 15
            reasons.append("Saturn aspecting 10th house")

    return {
        "trigger_score": trigger_score,
        "reasons": reasons
    }
