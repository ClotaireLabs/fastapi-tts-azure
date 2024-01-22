from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import io
from pydantic import BaseModel
import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

TTS_VOICE_NAME = "es-PE-CamilaNeural"
AUDIO_FOLDER = "audios"

load_dotenv()
speech_key = os.environ.get("SPEECH_KEY")
service_region = os.environ.get("SERVICE_REGION")

if not speech_key or not service_region:
    raise ValueError("Missing SPEECH_KEY or SERVICE_REGION")

speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_synthesis_voice_name = TTS_VOICE_NAME

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://gys-chatbot.vercel.app/",
        "https://chatbot-gys.vercel.app/",
        "http://localhost",
        "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/audios", StaticFiles(directory=os.path.abspath(AUDIO_FOLDER), html=True), name="audios")

class TextAndIdInput(BaseModel):
    id: str
    text: str

@app.post("/tts")

async def generate_wav(input_data: TextAndIdInput, request: Request):
    os.makedirs(AUDIO_FOLDER, exist_ok=True)
    output_file = os.path.join(AUDIO_FOLDER, f"{input_data.id}.wav")
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)

    text_input = input_data.text
    escaped_text = text_input.replace('&', '&amp;')

    text_template = """
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
        <voice name="{}">
            <mstts:express-as style="customerservice" styledegree="1.3" role="OlderAdultFemale">
                {}
            </mstts:express-as>
        </voice>
    </speak>
    """

    text = text_template.format(TTS_VOICE_NAME, escaped_text)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    try:
        result = speech_synthesizer.speak_ssml_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            audio_data = result.audio_data
            with open(output_file, "wb") as file:
                file.write(audio_data)
            audio_url = str(request.base_url.replace(scheme="http", path=f"/audios/{input_data.id}.wav"))
            # print(f"Audio URL: {audio_url}")

            return {"audio_url": audio_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
