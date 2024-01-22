import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from tts_generator import generate_wav, AUDIO_FOLDER

app = FastAPI()

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

app.mount("/{AUDIO_FOLDER}", StaticFiles(directory=os.path.abspath(AUDIO_FOLDER), html=True), name="{AUDIO_FOLDER}")

class TextAndIdInput(BaseModel):
    id: str
    text: str

@app.post("/tts")
async def tts_endpoint(input_data: TextAndIdInput, request: Request):
    try:
        audio_url = await generate_wav(input_data, request)
        return {"audio_url": audio_url}
    except HTTPException as e:
        raise e

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
