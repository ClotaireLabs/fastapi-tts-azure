import os
import hashlib
import requests
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

AZURE_KEY = os.getenv("AZURE_KEY")
AZURE_REGION = os.getenv("AZURE_REGION")
BASE_URL = os.getenv("BASE_URL", "")
API_KEY = os.getenv("API_KEY")

AUDIO_FOLDER = "static/audio"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

class TextAndIdInput(BaseModel):
    id: str
    text: str

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://gys-chatbot.vercel.app",
        "https://chatbot-gys.vercel.app",
        "http://localhost",
        "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for audio
app.mount("/static", StaticFiles(directory=os.path.abspath("static"), html=True), name="static")

# Optional root route
@app.get("/")
def root():
    return {"message": "Azure TTS API is running. Visit /docs to try it."}

# TTS generator
def synthesize_speech(text: str, voice: str = "en-US-AriaNeural", language: str = "en-US", filepath: str = ""):
    if not AZURE_KEY or not AZURE_REGION:
        raise HTTPException(status_code=500, detail="Azure credentials not set")

    endpoint = f"https://{AZURE_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_KEY,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3"
    }

    ssml = f"""
    <speak version='1.0' xml:lang='{language}'>
        <voice name='{voice}'>{text}</voice>
    </speak>
    """

    response = requests.post(endpoint, headers=headers, data=ssml.encode("utf-8"))
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Azure TTS failed: {response.text}")

    with open(filepath, "wb") as f:
        f.write(response.content)

# Main endpoint with API key check
@app.post("/tts", response_model=dict, summary="Generate TTS Audio", description="Generate TTS audio file (MP3) based on input text.")
async def tts_endpoint(
    input_data: TextAndIdInput,
    request: Request,
    x_api_key: str = Header(default=None)
):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid API key")

    try:
        # Generate audio hash
        hash_input = f"{input_data.id}:{input_data.text}"
        audio_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        audio_path = os.path.join(AUDIO_FOLDER, f"{audio_hash}.mp3")
        public_url = f"{BASE_URL}/static/audio/{audio_hash}.mp3" if BASE_URL else f"/static/audio/{audio_hash}.mp3"

        if not os.path.exists(audio_path):
            synthesize_speech(input_data.text, filepath=audio_path)

        return {"audio_url": public_url}

    except HTTPException as e:
        raise e

# Custom Swagger docs
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Azure TTS",
        version="0.0.1",
        description="This API generates TTS audio files with FastAPI and Azure Cognitive Services.",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
