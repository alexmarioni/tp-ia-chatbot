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

_CITY_PROMPT = """Extraé el nombre de la ciudad o lugar mencionado en el mensaje del usuario.
Si no se menciona ninguna ciudad concreta, respondé con "Buenos Aires".
Respondé SOLO con el nombre de la ciudad, sin explicación."""


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


def extract_city(message: str) -> str:
    response = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": _CITY_PROMPT},
            {"role": "user", "content": message},
        ],
        temperature=0,
        max_tokens=20,
    )
    return response.choices[0].message.content.strip()
