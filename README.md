# fastapi-tts-azure

This is an API for generating text-to-speech using Azure Cognitive Services. It utilizes FastAPI to create a simple and efficient interface for converting text to speech.

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

## Usage

1. Run the FastAPI server: `uvicorn main:app --reload`
2. Open your browser and go to `http://127.0.0.1:8000/docs` to view the Swagger documentation.
3. Use the provided endpoints to generate text-to-speech based on your requirements.
