'''

def build_prediction_prompt(chart, event_type):

    prediction = chart[f"{event_type}_prediction"]
    basic = chart["basic_details"]
    dasha = chart["dasha"]["current_mahadasha"]

    reasons = "\n".join([f"- {r}" for r in prediction["reasons"]])

    prompt = f"""
You are a professional Vedic astrologer.

Birth Overview:
- Lagna: {basic['lagna']}
- Current Mahadasha: {dasha}

Event: {event_type.capitalize()}
Score: {prediction['score']} / 100
Level: {prediction['level']}
Confidence: {prediction['confidence']}

Key Factors:
{reasons}

Instructions:
1. Provide a professional structured interpretation.
2. Explain strengths and weaknesses.
3. Give practical advice.
4. Do NOT invent planetary data.
5. Keep tone realistic and responsible.
"""

    return prompt
'''

def build_prediction_prompt(chart: dict, prediction_type: str) -> str:
    """
    Builds a controlled short-format astrology prediction prompt.

    Parameters:
        chart (dict): Full generated chart data
        prediction_type (str): 'marriage' or 'career'

    Returns:
        str: Optimized LLM prompt
    """

    prediction_data = chart.get(f"{prediction_type}_prediction", {})
    score = prediction_data.get("score", "N/A")
    level = prediction_data.get("level", "Unknown")
    reasons = prediction_data.get("reasons", [])

    # Limit reasons to 2 max (prevents token waste)
    short_reasons = reasons[:2]

    # Format reasons cleanly
    formatted_reasons = ", ".join(short_reasons) if short_reasons else "Planetary influences"

    prompt = f"""
You are AstroAI, a precise and professional Vedic astrologer.

Generate a SHORT astrology summary.

Rules:
- Maximum 5 lines only.
- Mention Score clearly.
- Mention Level (Strong / Moderate / Weak / Delayed).
- Mention 1–2 key astrological reasons.
- End with a clear one-line conclusion.
- No long paragraphs.
- No repetition.
- No storytelling.

Prediction Type: {prediction_type.capitalize()}
Score: {score}/100
Level: {level}
Key Factors: {formatted_reasons}

Respond in clean summary format.
"""

    return prompt.strip()