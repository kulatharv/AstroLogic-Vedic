import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_NINJAS_KEY")

def fetch_horoscope(sign: str):
    try:
        url = f"https://api.api-ninjas.com/v1/horoscope?zodiac={sign.lower()}"
        headers = {"X-Api-Key": API_KEY}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return {
                "status": "success",
                "sign": sign.capitalize(),
                "date": data.get("date"),
                "horoscope": data.get("horoscope")
            }
        else:
            return {
                "status": "error",
                "message": "Failed to fetch horoscope"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }