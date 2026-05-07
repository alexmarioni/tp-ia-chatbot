import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = Groq(api_key=os.environ["GROQ_API_KEY"])
_MODEL = "llama-3.1-8b-instant"

_INTENT_PROMPT = """Sos un clasificador de intents para un chatbot de clima.
Clasificá el mensaje del usuario en exactamente uno de estos intents:
- weather: el usuario quiere saber el clima o tiempo de algún lugar
- greeting: saludo inicial (hola, buenas, hey, etc.)
- goodbye: despedida (chau, hasta luego, adiós, etc.)
- chitchat: cualquier otro tema no relacionado con el clima

Respondé SOLO con el intent en minúsculas, sin explicación ni puntuación."""

_LOCATION_PROMPT = """Extraé la ubicación geográfica mencionada en el mensaje del usuario.
Respondé SOLO con un JSON válido con estas tres claves (sin texto extra):
- "city": nombre de la ciudad (si no hay ciudad concreta, "Buenos Aires")
- "province": provincia o estado (cadena vacía si no se menciona)
- "country": país (cadena vacía si no se menciona, inferí "Argentina" si el contexto lo sugiere)

Ejemplos:
Mensaje: "¿Cómo está el clima en Córdoba?" → {"city": "Córdoba", "province": "Córdoba", "country": "Argentina"}
Mensaje: "tiempo en Córdoba, España" → {"city": "Córdoba", "province": "Andalucía", "country": "España"}
Mensaje: "quiero saber el tiempo" → {"city": "Buenos Aires", "province": "Buenos Aires", "country": "Argentina"}"""


def classify(message: str) -> str:
    response = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": _INTENT_PROMPT},
            {"role": "user", "content": message},
        ],
        temperature=0,
        max_tokens=10,
    )
    intent = response.choices[0].message.content.strip().lower()
    valid = {"weather", "greeting", "goodbye", "chitchat"}
    return intent if intent in valid else "chitchat"


def extract_location(message: str) -> dict:
    """Retorna {"city": str, "province": str, "country": str}."""
    import json
    response = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": _LOCATION_PROMPT},
            {"role": "user", "content": message},
        ],
        temperature=0,
        max_tokens=60,
    )
    raw = response.choices[0].message.content.strip()
    try:
        data = json.loads(raw)
        return {
            "city": data.get("city", "Buenos Aires"),
            "province": data.get("province", ""),
            "country": data.get("country", ""),
        }
    except (json.JSONDecodeError, AttributeError):
        return {"city": raw, "province": "", "country": ""}
