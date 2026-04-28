import json
from astro_engine.llm_engine import ask_llm

def build_chat_prompt(chart, user_question):

    summary = {
        "lagna": chart["basic_details"]["lagna"],
        "current_dasha": chart["dasha"]["current_mahadasha"],
        "marriage_prediction": chart["marriage_prediction"],
        "career_prediction": chart["career_prediction"],
        "activated_houses": chart["activated_houses"],
        "advanced_yogas": chart["advanced_yogas"]
    }

    prompt = f"""
You are a professional Vedic astrologer.

Here is structured chart summary:
{json.dumps(summary, indent=2)}

User Question:
{user_question}

Instructions:
1. Answer only using provided data.
2. Do not invent new planetary positions.
3. Be professional and practical.
"""

    return prompt


def chat_with_chart(chart):

    print("\n🔮 Astrology Chat Mode Started")
    print("Type 'exit' to quit.\n")

    while True:
        user_question = input("You: ")

        if user_question.lower() == "exit":
            break

        prompt = build_chat_prompt(chart, user_question)
        response = ask_llm(prompt)

        print("\nAstroAI:", response)
        print("\n" + "-"*50 + "\n")
