import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from tts_generator import generate_wav, AUDIO_FOLDER

class TextAndIdInput(BaseModel):
    id: str
    text: str

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})


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

os.makedirs(AUDIO_FOLDER, exist_ok=True)
app.mount("/{AUDIO_FOLDER}", StaticFiles(directory=os.path.abspath(AUDIO_FOLDER), html=True), name="{AUDIO_FOLDER}")

@app.post("/tts", response_model=dict, summary="Generate TTS Audio", description="Generate TTS audio file (in WAV format) based on input text.")
async def tts_endpoint(input_data: TextAndIdInput, request: Request):
    try:
        audio_url = await generate_wav(input_data, request)
        return {"audio_url": audio_url}
    except HTTPException as e:
        raise e

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
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
