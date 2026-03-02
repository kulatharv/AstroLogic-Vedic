import requests

def ask_llm(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3",
                "prompt": prompt,
                "stream": False
            },
            timeout=5
        )

        return response.json().get("response", "No AI response")

    except Exception as e:
        print("AI ERROR:", e)
        return "AI service is not available in cloud deployment."
