import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from fastapi import HTTPException, Request
from pydantic import BaseModel

load_dotenv()

AUDIO_FOLDER = "audios"
TTS_VOICE_NAME = "es-PE-CamilaNeural"
SPEECH_KEY = os.environ.get("SPEECH_KEY")
SERVICE_REGION = os.environ.get("SERVICE_REGION")

if not SPEECH_KEY or not SERVICE_REGION:
    raise ValueError("Missing SPEECH_KEY or SERVICE_REGION")

speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SERVICE_REGION)
speech_config.speech_synthesis_voice_name = TTS_VOICE_NAME

async def generate_wav(input_data: BaseModel, request: Request):
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
            audio_url = str(request.base_url.replace(scheme="http", path=f"/{AUDIO_FOLDER}/{input_data.id}.wav"))
            return audio_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
