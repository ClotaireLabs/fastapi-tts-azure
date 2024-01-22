# fastapi-tts-azure

This is an API for generating text-to-speech using Azure Cognitive Services.

## Install

Run:

```python
pip install -r requirements.txt
```

## Config

Create a `.env` file:

```bash
SPEECH_KEY=your_key
SERVICE_REGION=your_region
```

## Obtaining Azure Cognitive Services Speech API Key

1. Visit the [Azure AI Services](https://azure.microsoft.com/en-us/products/ai-services/ai-speech) page.
2. Create a new resource in Azure by selecting "Speech service".
3. In the resource's dashboard, navigate to the "Keys and endpoint" section.
4. Find "KEY 1". This is your `SPEECH_KEY`.
5. Locate the "Location/Region" info. This is your `SERVICE_REGION`.

## Usage

1. Run the FastAPI server: `uvicorn main:app --reload`
2. Open your browser and go to `http://127.0.0.1:8000/docs` to view the Swagger documentation.
3. Use the provided endpoints to generate text-to-speech based on your requirements.

## Custom TTS Voice

- [Supported languages](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support) of Azure Speech service.
- How to custom [speaking styles and roles](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-voice).

## API Documentation

- [Documentation](https://fastapi-tts-azure.onrender.com/docs) made with Swagger.
