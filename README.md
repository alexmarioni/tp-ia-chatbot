# Chatbot de Clima — TP Inteligencia Artificial

Chatbot conversacional que consulta el clima en tiempo real, detecta chit-chat y maneja el silencio del usuario.

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | Flutter (Windows Desktop) |
| Backend | Python + FastAPI |
| LLM (clasificación + respuestas) | Groq API — `llama-3.1-8b-instant` (gratuito) |
| Datos de clima | Open-Meteo (sin API key, sin registro) |

## Funcionalidades

- **Consulta de clima**: preguntá el tiempo en cualquier ciudad, provincia o país del mundo (con o sin tildes/mayúsculas)
- **Geolocalización**: botón 📍 para consultar el clima en tu ubicación actual
- **Chit-chat contextual**: el bot responde de forma adaptada al tono (hasta 3 veces por sesión)
- **No-input**: si el usuario no responde en 30 segundos, el bot advierte; a los 15 segundos cierra la sesión automáticamente
- **Reconexión automática**: si el backend no está listo, la app lo detecta y espera automáticamente

---

## Instrucciones para el profesor

### Requisitos previos

- **Python 3.10+** — [descargar](https://www.python.org/downloads/)
- **API key de Groq** (gratuita, sin tarjeta de crédito) — [obtener en console.groq.com](https://console.groq.com)

> Flutter **no es necesario** si el EXE ya está compilado en `flutter_app/build/windows/x64/runner/Release/`.

### Paso 1 — Clonar el repositorio

```bash
git clone https://github.com/alexmarioni/tp-ia-chatbot.git
cd tp-ia-chatbot
```

### Paso 2 — Crear el archivo de configuración

Dentro de la carpeta `backend/`, crear un archivo llamado `.env` con el siguiente contenido:

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Reemplazar `gsk_xxx...` con tu API key de Groq.

### Paso 3 — Ejecutar

Hacer **doble click** en `iniciar.ps1` (o click derecho → *Ejecutar con PowerShell*).

El script hace todo automáticamente:
1. Verifica Python y crea el entorno virtual
2. Instala las dependencias del backend
3. Abre el backend en una ventana separada
4. Lanza la aplicación Flutter

> Si aparece un error de permisos en PowerShell, ejecutar primero en una terminal de administrador:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

---

## Instrucciones para desarrolladores

### Requisitos

- Python 3.10+
- Flutter 3.x — [instalar](https://flutter.dev/docs/get-started/install)
- Cuenta gratuita en [console.groq.com](https://console.groq.com)

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Crear backend/.env con GROQ_API_KEY=gsk_...

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd flutter_app
flutter pub get
flutter run -d windows

# Para compilar el EXE de distribución:
flutter build windows --release
```

---

## Estructura del proyecto

```
tp-ia-chatbot/
├── iniciar.ps1                   # Script de inicio unificado (profesor)
├── start_backend.ps1             # Script solo para el backend
├── backend/
│   ├── main.py                   # FastAPI — endpoints /chat, /weather/coords, /session, /health
│   ├── intent_classifier.py      # Clasificación de intents + extracción de ubicación (Groq)
│   ├── weather_service.py        # Consulta de clima (Open-Meteo)
│   ├── session_manager.py        # Sesiones, timeout y límite de chit-chat
│   └── requirements.txt
└── flutter_app/
    └── lib/
        ├── main.dart
        ├── screens/chat_screen.dart    # UI principal + timers + health check
        ├── widgets/message_bubble.dart
        └── services/chat_service.dart  # HTTP al backend
```

## Endpoints del Backend

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/chat` | Enviar mensaje al chatbot |
| `POST` | `/weather/coords` | Consultar clima por coordenadas GPS |
| `DELETE` | `/session/{id}` | Cerrar sesión |
| `GET` | `/health` | Estado del servidor |

### Ejemplo de consulta

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123", "message": "clima en Mendoza"}'
```

```json
{
  "reply": "📍 Mendoza, Mendoza, Argentina\n☀️ Cielo despejado\n\n🌞 Temperatura: 24°C\n💧 Humedad: 35%\n💨 Viento: 18 km/h\n🌂 Prob. de lluvia: 0%",
  "intent": "weather",
  "session_active": true
}
```
