import os
from groq import Groq
from dotenv import load_dotenv
from session_manager import MAX_CHITCHATS

load_dotenv()

_client = Groq(api_key=os.environ["GROQ_API_KEY"])
_MODEL = "llama-3.1-8b-instant"

_INTENT_PROMPT = """Sos un clasificador de intents para un chatbot de clima.
Clasificá el mensaje del usuario en exactamente uno de estos intents:

- weather: el usuario quiere saber el clima de algún lugar. Incluye TODOS estos casos:
  * Preguntas explícitas ("¿cómo está el clima en X?", "¿va a llover en X?", "tiempo en X")
  * Solo un nombre de lugar, con o sin tildes, con o sin mayúsculas ("cordoba", "entre rios", "villa del rosario")
  * Nombre de lugar + provincia o país ("gobernador racedo entre rios", "cordoba argentina")
  * Nombres de ciudades o pueblos poco conocidos o inusuales: si parece un nombre propio geográfico, es weather

- greeting: saludo sin consulta de clima ("hola", "buenas", "hey", "¿cómo estás?", "buen día")

- goodbye: despedida ("chau", "hasta luego", "adiós", "nos vemos", "bye")

- chitchat: tema que claramente NO es un lugar ni un saludo (comentarios, insultos, preguntas personales, comida, deportes, etc.)

REGLA CRÍTICA: Si el mensaje es o podría ser un nombre de ciudad, pueblo, provincia o país,
clasificalo como "weather" aunque le falten tildes, mayúsculas o palabras como "clima" o "tiempo".
Ante la duda entre "weather" y "chitchat", siempre elegí "weather".

Ejemplos:
"gobernador racedo entre rios" → weather
"Gobernador Racedo, Entre Ríos" → weather
"cordoba" → weather
"villa del rosario córdoba" → weather
"hola" → greeting
"tengo hambre" → chitchat
"chau" → goodbye
"me gusta el fútbol" → chitchat

Respondé SOLO con el intent en minúsculas, sin explicación ni puntuación."""

_LOCATION_PROMPT = """Extraé la ubicación geográfica mencionada en el mensaje del usuario.
El mensaje puede estar mal escrito, sin tildes o en minúsculas: normalizá el nombre correctamente.
Respondé SOLO con un JSON válido con estas tres claves (sin texto extra):
- "city": nombre de la ciudad o pueblo con ortografía correcta y mayúsculas
- "province": provincia o estado con ortografía correcta (cadena vacía si no se puede inferir)
- "country": país con ortografía correcta (inferí "Argentina" si el contexto lo sugiere, vacío si es de otro país)

Ejemplos:
"¿Cómo está el clima en Córdoba?" → {"city": "Córdoba", "province": "Córdoba", "country": "Argentina"}
"gobernador racedo entre rios" → {"city": "Gobernador Racedo", "province": "Entre Ríos", "country": "Argentina"}
"villa del rosario cordoba" → {"city": "Villa del Rosario", "province": "Córdoba", "country": "Argentina"}
"tiempo en cordoba españa" → {"city": "Córdoba", "province": "Andalucía", "country": "España"}
"quiero saber el tiempo" → {"city": "Buenos Aires", "province": "Buenos Aires", "country": "Argentina"}"""


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
