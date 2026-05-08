import httpx

_GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

_WMO_CODES = {
    0: "Cielo despejado",
    1: "Mayormente despejado", 2: "Parcialmente nublado", 3: "Nublado",
    45: "Niebla", 48: "Niebla con escarcha",
    51: "Llovizna leve", 53: "Llovizna moderada", 55: "Llovizna intensa",
    61: "Lluvia leve", 63: "Lluvia moderada", 65: "Lluvia intensa",
    71: "Nieve leve", 73: "Nieve moderada", 75: "Nieve intensa",
    80: "Chubascos leves", 81: "Chubascos moderados", 82: "Chubascos intensos",
    95: "Tormenta eléctrica", 99: "Tormenta con granizo",
}

_WMO_EMOJIS = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
    45: "🌫️", 48: "🌫️",
    51: "🌦️", 53: "🌦️", 55: "🌧️",
    61: "🌧️", 63: "🌧️", 65: "🌧️",
    71: "🌨️", 73: "🌨️", 75: "❄️",
    80: "🌦️", 81: "🌦️", 82: "⛈️",
    95: "⛈️", 99: "⛈️",
}

_WEATHER_PARAMS = "temperature_2m,relative_humidity_2m,weathercode,windspeed_10m,precipitation_probability"


def _temp_emoji(temp: float) -> str:
    if temp < 0:   return "🥶"
    if temp < 10:  return "🧥"
    if temp < 20:  return "😊"
    if temp < 30:  return "🌞"
    return "🥵"


def _format_reply(current: dict, display_name: str) -> str:
    temp     = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    wind     = current["windspeed_10m"]
    rain     = current.get("precipitation_probability", 0)
    code     = current["weathercode"]
    condition    = _WMO_CODES.get(code, "Condición desconocida")
    weather_icon = _WMO_EMOJIS.get(code, "🌡️")
    rain_icon    = "☔" if rain >= 60 else "🌂"

    return (
        f"📍 {display_name}\n"
        f"{weather_icon} {condition}\n"
        f"\n"
        f"{_temp_emoji(temp)} Temperatura:    {temp}°C\n"
        f"💧 Humedad:       {humidity}%\n"
        f"💨 Viento:        {wind} km/h\n"
        f"{rain_icon} Prob. de lluvia: {rain}%"
    )


async def get_weather(city: str, province: str = "", country: str = "") -> str:
    # Construye query combinando ciudad + provincia + país para máxima precisión
    parts = [p for p in [city, province, country] if p]
    query = ", ".join(parts)

    async with httpx.AsyncClient(timeout=10) as client:
        geo = await client.get(_GEO_URL, params={"name": query, "count": 3, "language": "es"})
        geo.raise_for_status()
        results = geo.json().get("results")

        if not results:
            # Segundo intento solo con ciudad si el query completo no dio resultados
            if len(parts) > 1:
                geo2 = await client.get(_GEO_URL, params={"name": city, "count": 1, "language": "es"})
                results = geo2.json().get("results")
            if not results:
                return f"No encontré '{query}'. ¿Podés especificar mejor la ubicación?"

        # Elige el resultado que mejor coincida con provincia/país indicados
        loc = _best_match(results, province, country)
        lat, lon = loc["latitude"], loc["longitude"]

        # Construye nombre para mostrar con admin1 (provincia) y país de la respuesta
        loc_city = loc.get("name", city)
        loc_admin1 = loc.get("admin1", province)
        loc_country = loc.get("country", country)
        display_parts = [p for p in [loc_city, loc_admin1, loc_country] if p]
        display_name = ", ".join(display_parts)

        weather = await client.get(_WEATHER_URL, params={
            "latitude": lat,
            "longitude": lon,
            "current": _WEATHER_PARAMS,
            "timezone": "auto",
        })
        weather.raise_for_status()
        current = weather.json()["current"]

    return _format_reply(current, display_name)


async def get_weather_by_coords(lat: float, lon: float) -> str:
    async with httpx.AsyncClient(timeout=10) as client:
        weather = await client.get(_WEATHER_URL, params={
            "latitude": lat,
            "longitude": lon,
            "current": _WEATHER_PARAMS,
            "timezone": "auto",
        })
        weather.raise_for_status()
        current = weather.json()["current"]

    return _format_reply(current, "tu ubicación actual")


def _best_match(results: list, province: str, country: str) -> dict:
    """Prioriza el resultado que coincida con provincia y/o país indicados."""
    if not province and not country:
        return results[0]

    province_lower = province.lower()
    country_lower = country.lower()

    for r in results:
        r_admin1 = r.get("admin1", "").lower()
        r_country = r.get("country", "").lower()
        province_match = province_lower and province_lower in r_admin1
        country_match = country_lower and country_lower in r_country
        if province_match and country_match:
            return r
    for r in results:
        r_country = r.get("country", "").lower()
        if country_lower and country_lower in r_country:
            return r

    return results[0]
