from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import intent_classifier as classifier
import weather_service as weather
import session_manager as sessions

app = FastAPI(title="Chatbot de Clima")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    intent: str
    session_active: bool


_CHITCHAT_REPLY = (
    "Entiendo, pero estoy especializado en consultas de clima. "
    "¿Querés saber el tiempo en alguna ciudad?"
)
_GREETING_REPLY = (
    "¡Hola! Soy tu asistente de clima. "
    "Podés preguntarme el tiempo en cualquier ciudad del mundo. "
    "Por ejemplo: '¿Cómo está el clima en Mendoza?'"
)
_GOODBYE_REPLY = "¡Hasta luego! Que tengas un buen día."


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not sessions.is_active(req.session_id):
        raise HTTPException(status_code=410, detail="Sesión cerrada.")

    sessions.touch(req.session_id)
    message = req.message.strip()

    if not message:
        return ChatResponse(
            reply="No escuché nada. ¿En qué ciudad querés consultar el clima?",
            intent="empty",
            session_active=True,
        )

    intent = classifier.classify(message)

    if intent == "weather":
        city = classifier.extract_city(message)
        reply = await weather.get_weather(city)
    elif intent == "greeting":
        reply = _GREETING_REPLY
    elif intent == "goodbye":
        sessions.close_session(req.session_id)
        return ChatResponse(reply=_GOODBYE_REPLY, intent="goodbye", session_active=False)
    else:
        reply = _CHITCHAT_REPLY

    return ChatResponse(reply=reply, intent=intent, session_active=True)


@app.delete("/session/{session_id}")
async def close_session(session_id: str):
    sessions.close_session(session_id)
    return {"detail": "Sesión cerrada por inactividad."}


@app.get("/health")
async def health():
    return {"status": "ok"}
