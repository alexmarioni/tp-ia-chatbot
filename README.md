# Chatbot de Clima — TP Inteligencia Artificial

Chatbot conversacional que consulta el clima en tiempo real mediante Open-Meteo, detecta chit-chat y maneja el silencio del usuario.

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | Flutter |
| Backend | Python + FastAPI |
| LLM (intents + respuestas) | Groq API — `llama-3.1-8b-instant` (gratuito) |
| Datos de clima | Open-Meteo (sin API key) |

## Funcionalidades

- **Consulta de clima**: el usuario puede preguntar por el tiempo en cualquier ciudad del mundo
- **Chit-chat**: si el usuario habla de otro tema, el bot lo detecta y redirige la conversación
- **No-input**: si el usuario no responde en 30 segundos, el bot advierte; a los 15 segundos adicionales cierra la sesión automáticamente

## Requisitos previos

- Python 3.10+
- Flutter 3.x ([instalar](https://flutter.dev/docs/get-started/install))
- Cuenta gratuita en [console.groq.com](https://console.groq.com) para obtener una API key

## Setup del Backend

```bash
cd backend

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
.venv\Scripts\activate         # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu GROQ_API_KEY

# Iniciar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Setup del Frontend (Flutter)

```bash
cd flutter_app

# Instalar dependencias
flutter pub get

# Configurar la URL del backend
# Editar lib/services/chat_service.dart y cambiar baseUrl:
#   - Emulador Android: http://10.0.2.2:8000
#   - Dispositivo físico: http://<IP_DE_TU_PC>:8000
#   - Web/Desktop: http://localhost:8000

# Correr la app
flutter run
```

## Estructura del proyecto

```
ia-chatbot/
├── backend/
│   ├── main.py               # FastAPI app
│   ├── intent_classifier.py  # Clasificación de intents con Groq
│   ├── weather_service.py    # Consulta de clima con Open-Meteo
│   ├── session_manager.py    # Manejo de sesiones
│   └── requirements.txt
└── flutter_app/
    └── lib/
        ├── main.dart
        ├── screens/chat_screen.dart
        ├── widgets/message_bubble.dart
        └── services/chat_service.dart
```

## Endpoints del Backend

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/chat` | Enviar mensaje al chatbot |
| `DELETE` | `/session/{id}` | Cerrar sesión por inactividad |

### Ejemplo de request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123", "message": "¿Cómo está el clima en Córdoba?"}'
```

### Ejemplo de response

```json
{
  "reply": "En Córdoba la temperatura actual es de 18°C, con cielo parcialmente nublado. La probabilidad de lluvia es del 20%.",
  "intent": "weather",
  "session_active": true
}
```
