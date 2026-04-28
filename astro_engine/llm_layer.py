# astro_engine/llm_layer.py


def build_llm_prompt(chart, event_type):

    explanation = chart.get(f"{event_type}_explanation", "")
    prediction = chart.get(f"{event_type}_prediction", {})

    prompt = f"""
You are an experienced Vedic astrologer.

Below is structured astrology analysis.

Event Type: {event_type}
Score: {prediction.get("score")}
Level: {prediction.get("level")}

Structured Explanation:
{explanation}

Instructions:
- Convert this into a natural, professional astrology consultation.
- Do NOT change numerical logic.
- Do NOT invent new planetary placements.
- Keep interpretation grounded in provided facts.
- Avoid exaggeration.
- Provide balanced tone.

Final Answer:
"""

    return prompt
