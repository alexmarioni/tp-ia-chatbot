import os
from groq import Groq
from dotenv import load_dotenv
from session_manager import MAX_CHITCHATS

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


_CHITCHAT_SYSTEM = """Sos un asistente virtual especializado en clima, amigable pero enfocado.
El usuario dijo algo fuera del tema clima. Respondé en 1-2 oraciones cortas adaptando el tono:
- Saludo o pregunta personal ("¿cómo estás?"): respondé cálidamente
- Insulto o queja agresiva ("¡idiota!"): respondé con calma, sin confrontar, sin disculparte de más
- Comentario random ("tengo hambre", "me gusta el fútbol"): respondé con humor leve o empatía
- Siempre terminá redirigiendo al clima. Sé natural y variado, no uses frases genéricas.
{limit_hint}"""

_CHITCHAT_LIMIT_HINT = "Además, avisá amablemente que es tu última respuesta fuera del tema."

_GREETING_SYSTEM = """Sos un asistente de clima amigable. El usuario te saludó.
Respondé con un saludo cálido y breve (1-2 oraciones). Presentate como asistente de clima
y sugerí cómo usarte con un ejemplo concreto de ciudad. Sé natural y variado."""


def generate_chitchat_reply(message: str, count: int) -> str:
    hint = _CHITCHAT_LIMIT_HINT if count >= MAX_CHITCHATS else ""
    system = _CHITCHAT_SYSTEM.format(limit_hint=hint).strip()
    response = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": message},
        ],
        temperature=0.7,
        max_tokens=80,
    )
    return response.choices[0].message.content.strip()


def generate_greeting_reply(message: str) -> str:
    response = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": _GREETING_SYSTEM},
            {"role": "user", "content": message},
        ],
        temperature=0.7,
        max_tokens=80,
    )
    return response.choices[0].message.content.strip()


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
