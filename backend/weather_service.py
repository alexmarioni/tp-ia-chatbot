import httpx

_GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

_WMO_CODES = {
    0: "cielo despejado",
    1: "mayormente despejado", 2: "parcialmente nublado", 3: "nublado",
    45: "niebla", 48: "niebla con escarcha",
    51: "llovizna leve", 53: "llovizna moderada", 55: "llovizna intensa",
    61: "lluvia leve", 63: "lluvia moderada", 65: "lluvia intensa",
    71: "nieve leve", 73: "nieve moderada", 75: "nieve intensa",
    80: "chubascos leves", 81: "chubascos moderados", 82: "chubascos intensos",
    95: "tormenta eléctrica", 99: "tormenta con granizo",
}


async def get_weather(city: str) -> str:
    async with httpx.AsyncClient(timeout=10) as client:
        geo = await client.get(_GEO_URL, params={"name": city, "count": 1, "language": "es"})
        geo.raise_for_status()
        results = geo.json().get("results")
        if not results:
            return f"No encontré la ciudad '{city}'. ¿Podés especificar mejor el nombre?"

        loc = results[0]
        lat, lon = loc["latitude"], loc["longitude"]
        name = loc.get("name", city)
        country = loc.get("country", "")

        weather = await client.get(_WEATHER_URL, params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weathercode,windspeed_10m,precipitation_probability",
            "timezone": "auto",
        })
        weather.raise_for_status()
        current = weather.json()["current"]

    temp = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    wind = current["windspeed_10m"]
    rain_prob = current.get("precipitation_probability", 0)
    condition = _WMO_CODES.get(current["weathercode"], "condición desconocida")

    return (
        f"En {name}, {country} hay {condition}. "
        f"Temperatura: {temp}°C | Humedad: {humidity}% | "
        f"Viento: {wind} km/h | Probabilidad de lluvia: {rain_prob}%."
    )
