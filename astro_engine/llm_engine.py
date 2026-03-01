'''
import requests

def ask_llm(prompt):

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi3",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                #"num_predict": 150,      # LIMIT RESPONSE LENGTH
                "top_p": 0.9,
                "repeat_penalty": 1.1
            }
        }
    )
    payload = {
    "model": "phi3",
    "prompt": prompt,
    "stream": False,
    "options": {
        "temperature": 0.6,
        "top_p": 0.9,
        "num_predict": 200
    }
}
    #return response.json()["response"]
    data = response.json()

    print("🔎 LLM RAW RESPONSE:", data)

    if "response" in data:
        return data["response"]

    elif "message" in data:
        return data["message"]

    elif "choices" in data:   # for OpenAI-style response
        return data["choices"][0]["message"]["content"]

    else:
        return f"LLM Error: Unexpected response format -> {data}"


        '''
import requests

def ask_llm(prompt):

    payload = {
        "model": "phi3",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.6,
            "num_predict": 250
        }
    }

    response = requests.post("http://localhost:11434/api/generate", json=payload)

    data = response.json()

    print("🔎 LLM RAW RESPONSE:", data.get("response"))

    if "response" in data:
        return data["response"]
    else:
        return f"LLM Error: {data}"