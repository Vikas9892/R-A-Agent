import logging
import httpx
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Geocoding and weather API endpoints (Open-Meteo provides free, keyless weather data)
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


@tool
def get_weather(city: str) -> str:
    """Fetch current weather for a specified city or location.

    Input: Name of the city (e.g. 'Tokyo', 'London', 'San Francisco').
    Output: Summary of temperature, windspeed, and weather condition.
    """
    clean_city = city.strip()
    if not clean_city:
        return "Error: City name cannot be empty."

    try:
        with httpx.Client(timeout=10.0) as client:
            # Step 1: Resolve city to coordinates
            geo_resp = client.get(GEOCODING_URL, params={"name": clean_city, "count": 1})
            geo_resp.raise_for_status()
            geo_data = geo_resp.json()

            results = geo_data.get("results")
            if not results:
                return f"Could not locate weather data for '{clean_city}'."

            location = results[0]
            lat = location.get("latitude")
            lon = location.get("longitude")
            name = location.get("name", clean_city)
            country = location.get("country", "")

            # Step 2: Fetch current weather for coordinates
            weather_resp = client.get(
                FORECAST_URL,
                params={"latitude": lat, "longitude": lon, "current_weather": "true"},
            )
            weather_resp.raise_for_status()
            weather_data = weather_resp.json()

            current = weather_data.get("current_weather", {})
            temp = current.get("temperature")
            wind = current.get("windspeed")

            return (
                f"Weather in {name}, {country}: {temp}°C, "
                f"windspeed {wind} km/h."
            )
    except Exception as exc:
        logger.error("Weather lookup failed for '%s': %s", clean_city, exc)
        return f"Error retrieving weather for '{clean_city}': {exc}"
