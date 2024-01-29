import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from fastapi import HTTPException, Request
from pydantic import BaseModel

load_dotenv()

AUDIO_FOLDER = "audios"
TTS_VOICE_NAME = "es-PE-CamilaNeural"

def setup_speech_config():
    key = os.environ.get("SPEECH_KEY")
    region = os.environ.get("SERVICE_REGION")

    if not key or not region:
        raise ValueError("Missing SPEECH_KEY or SERVICE_REGION")

    config = speechsdk.SpeechConfig(subscription=key, region=region)
    config.speech_synthesis_voice_name = TTS_VOICE_NAME
    return config

speech_config = setup_speech_config()

def synthesize_speech(text, audio_config):
    text_template = """
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="es-PE">
        <voice name="{}">
            <mstts:express-as style="customerservice" styledegree="1" role="OlderAdultFemale">
                {}
            </mstts:express-as>
        </voice>
    </speak>
    """

    formatted_text = text_template.format(TTS_VOICE_NAME, text)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    try:
        result = synthesizer.speak_ssml_async(formatted_text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    return False

async def generate_wav(input_data: BaseModel, request: Request):
    output_file = os.path.join(AUDIO_FOLDER, f"{input_data.id}.wav")
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)

    escaped_text = input_data.text.replace('&', '&amp;')

    if synthesize_speech(escaped_text, audio_config):
        audio_url = str(request.base_url.replace(scheme="http", path=f"/{AUDIO_FOLDER}/{input_data.id}.wav"))
        return audio_url

    raise HTTPException(status_code=500, detail="Failed to generate audio")
