# astro_engine/explanation_builder.py


def build_event_explanation(chart, event_type):

    explanation = []
    prediction = chart.get(f"{event_type}_prediction", {})
    strengths = chart.get("planet_strength_scores", {})
    yogas = chart.get("advanced_yogas", [])
    activated = chart.get("activated_houses", [])
    transits = chart.get("current_transits", {})
    house_lords = chart.get("house_lords", {})

    if not prediction:
        return "Prediction data not available."

    score = prediction.get("score", 0)
    level = prediction.get("level", "Unknown")
    reasons = prediction.get("reasons", [])

    explanation.append(f"{event_type.capitalize()} outlook is classified as '{level}' with a score of {score}/100.\n")

    # Core reasons from scoring engine
    explanation.append("Key contributing factors:")
    for r in reasons:
        explanation.append(f"- {r}")

    explanation.append("")

    # ---------------------------------
    # Event-specific interpretation
    # ---------------------------------

    if event_type == "marriage":

        seventh_lord = house_lords[7]["lord"]
        lord_strength = strengths.get(seventh_lord, 0.5)
        venus_strength = strengths.get("Venus", 0.5)

        explanation.append(f"7th lord ({seventh_lord}) strength: {lord_strength}")
        explanation.append(f"Venus strength (relationship significator): {venus_strength}")

        if 7 in activated:
            explanation.append("Current dasha period activates the 7th house, increasing relationship probability.")

        if transits.get("Jupiter", {}).get("house_from_lagna") == 7:
            explanation.append("Jupiter transit over the 7th house enhances commitment and partnership growth.")

        if "Raj Yoga" in yogas:
            explanation.append("Presence of Raj Yoga supports stability and long-term alignment.")

    elif event_type == "career":

        tenth_lord = house_lords[10]["lord"]
        lord_strength = strengths.get(tenth_lord, 0.5)
        saturn_strength = strengths.get("Saturn", 0.5)

        explanation.append(f"10th lord ({tenth_lord}) strength: {lord_strength}")
        explanation.append(f"Saturn strength (career discipline): {saturn_strength}")

        if 10 in activated:
            explanation.append("Current dasha period activates the 10th house, indicating career movement.")

        if transits.get("Jupiter", {}).get("house_from_lagna") == 10:
            explanation.append("Jupiter transit over the 10th house supports growth and recognition.")

        if "Raj Yoga" in yogas:
            explanation.append("Raj Yoga enhances authority and professional status potential.")

    # ---------------------------------
    # Final Interpretation Summary
    # ---------------------------------

    if score >= 75:
        summary = "Overall, conditions are highly supportive."
    elif score >= 55:
        summary = "Overall, conditions are favorable with moderate effort required."
    elif score >= 35:
        summary = "Results are possible but may require patience and corrective action."
    else:
        summary = "Conditions suggest delay or obstacles at present."

    explanation.append("")
    explanation.append(summary)

    return "\n".join(explanation)
