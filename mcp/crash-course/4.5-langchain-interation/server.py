import httpx
import asyncio
import json
from mcp.server.fastmcp import FastMCP

server = FastMCP(
    name="weather",
    host="0.0.0.0",
    port=4567
)


@server.tool()
async def get_state_and_qrid(longitude: str, latitude: str) -> str:
    """Retrieve the state name and grid info for a given location.

    Args:
        longitude (str): The longitude of the location.
        latitude (str): The latitude of the location.
    """

    USER_AGENT = "weather-app/1.0"
    weather_api_url = "https://api.weather.gov/points/"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{weather_api_url}{latitude},{longitude}",
                headers=headers,
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                props = data.get("properties", {})
                state = props.get("gridId", "Unknown")
                gridx = props.get("gridX", "Unknown")
                gridy = props.get("gridY", "Unknown")
                ret = {
                    "state": state,
                    "gridx": gridx,
                    "gridy": gridy
                }

                print(f"Retrieved state: {state}, gridX: {gridx}, gridY: {gridy}")
                return json.dumps(ret)
            else:
                return json.dumps({"error": f"Unable to retrieve weather data. Status: {response.status_code}"})
                
    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    # Default to SSE for easy testing
    server.run(transport="sse")

