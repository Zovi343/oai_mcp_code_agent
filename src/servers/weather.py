import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Initialize FastMCP server for Weather tools (SSE)
mcp = FastMCP("weather", port=os.getenv('WEATHER_API_PORT'))

@mcp.tool()
async def get_forecast(location: str) -> str:
    """Get weather forecast for a location or address.

    Args:
        location: Location name or address.

    Returns:
        A string containing a single weather forecast for the location.
    """
    location_lower = location.lower()

    if "toronto" in location_lower:
        period = {
            "name": "Today",
            "temperature": 15,
            "temperatureUnit": "C",
            "windSpeed": "20 km/h",
            "windDirection": "NW",
            "detailedForecast":
                "Cloudy with a chance of light showers in the evening.",
        }
    elif "london" in location_lower:
        period = {
            "name": "Today",
            "temperature": 12,
            "temperatureUnit": "C",
            "windSpeed": "15 km/h",
            "windDirection": "SW",
            "detailedForecast":
                "Overcast skies with periods of drizzle throughout the day.",
        }
    elif "seattle" in location_lower:
        period = {
            "name": "Today",
            "temperature": 13,
            "temperatureUnit": "C",
            "windSpeed": "18 km/h",
            "windDirection": "W",
            "detailedForecast":
                "Rainy and cool with occasional breaks in the clouds.",
        }
    else:
        period = {
            "name": "Today",
            "temperature": 16,
            "temperatureUnit": "C",
            "windSpeed": "10 km/h",
            "windDirection": "E",
            "detailedForecast":
                "Mild weather with variable cloudiness.",
        }

    forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
    return forecast

if __name__ == "__main__":
    mcp.run(transport="sse")
