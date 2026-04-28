
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

        
"""
Horoscope Service - Uses local horoscope_engine.py instead of external API
"""
'''
import sys
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Add the astro_engine directory to Python path
current_dir = Path(__file__).parent.parent
astro_engine_path = current_dir / "astro_engine"
sys.path.insert(0, str(astro_engine_path))

print(f"🔍 Looking for horoscope_engine.py in: {astro_engine_path}")

try:
    # Import from horoscope_engine.py
    from astro_engine.horoscope_engine import generate_horoscope
    print("✅ Successfully loaded horoscope_engine.py")
except ImportError as e:
    print(f"❌ Failed to import horoscope_engine: {e}")
    # Fallback to festival_engine if needed
    try:
        from astro_engine.festival_engine import generate_horoscope
        print("✅ Successfully loaded festival_engine.py as fallback")
    except ImportError:
        print("❌ No horoscope engine found!")
        raise

# Thread pool for async operations
_executor = ThreadPoolExecutor(max_workers=4)

async def fetch_horoscope(sign: str) -> dict:
    """
    Fetch horoscope using local horoscope_engine.py
    
    Args:
        sign: Zodiac sign (lowercase, e.g., 'aries')
    
    Returns:
        Dictionary with complete horoscope data
    """
    try:
        # Convert sign to proper case for the engine
        sign_proper = sign.capitalize()
        
        # Run the synchronous generate_horoscope in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(_executor, generate_horoscope, sign_proper)
        
        # Ensure all required fields are present
        if "stars" in result:
            # Convert star ratings to display format if needed
            result["stars_display"] = {
                k: '★' * round(v) + '☆' * (5 - round(v))
                for k, v in result["stars"].items()
            }
        
        # Add sign info
        result["sign_lower"] = sign.lower()
        
        return result
    except Exception as e:
        print(f"❌ Error in fetch_horoscope: {e}")
        import traceback
        traceback.print_exc()
        
        # Return graceful error response
        return {
            "sign": sign.capitalize(),
            "error": str(e),
            "overview": f"Unable to calculate planetary positions at this moment. Please ensure Swiss Ephemeris files are available.",
            "love": "Check your connection and try again later.",
            "career": "The cosmic data is temporarily unavailable.",
            "health": "Please refresh the page in a few moments.",
            "stars": {"overall": 2.5, "love": 2.5, "career": 2.5, "health": 2.5, "finance": 2.5, "luck": 2.5},
            "stars_display": {"overall": "★★★☆☆", "love": "★★★☆☆", "career": "★★★☆☆", "health": "★★★☆☆", "finance": "★★★☆☆", "luck": "★★★☆☆"},
            "tithi": "Calculating...",
            "moon_nakshatra": "Loading",
            "moon_sign": "Loading",
            "sun_sign": "Loading",
            "lucky_number": 7,
            "lucky_color": "Gold",
            "lucky_gem": "Ruby",
            "ruling_planet": "Mars",
            "best_time": "Morning",
            "mantra": "Om Namah Shivaya",
            "tip": "Stay grounded and trust your intuition.",
            "compatible": ["Leo", "Sagittarius", "Gemini"],
            "key_transits": ["Planetary positions being calculated..."]
        }
    '''