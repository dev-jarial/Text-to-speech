import requests
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.staticfiles import StaticFiles

app = FastAPI()
# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

templates = Jinja2Templates(directory="templates")
ELEVENLABS_API_KEY = '0f40658ff5948ef90cd180b816da4c79'


@app.get("/upload", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, name: str = Form(...), file: UploadFile = File(...)):
    url = "https://api.elevenlabs.io/v1/voices/add"
    
    payload = {'name': name}
    files = [
        ('files', (file.filename, file.file.read(), 'audio/mpeg'))
    ]
    headers = {
        'xi-api-key': ELEVENLABS_API_KEY
    }

    try:
        response = requests.post(url, headers=headers, data=payload, files=files)
        response.raise_for_status()  # Raise an exception for HTTP error status codes
        response_json = response.json()  # Parse JSON response
        voice_id = response_json.get('voice_id')  # Extract voice_id value
        # print(voice_id,"----------")
        return templates.TemplateResponse("text_speech.html", {"request": request, "voice_id": voice_id})
    except requests.exceptions.RequestException as e:
        return templates.TemplateResponse("text_speech.html", {"request": request, "error_message": str(e)})

@app.get("/text_speech", response_class=HTMLResponse)
async def text_speech_webpage(request: Request):
    return templates.TemplateResponse("text_speech.html", {"request": request})
from pydantic import BaseModel

class TextToSpeechInput(BaseModel):
    text: str
    model_id: str
    voice_settings: dict

@app.post("/text_speech/{voice_id}", response_class=HTMLResponse)
def text_speech_webpage(request: Request, voice_id: str, input_data: TextToSpeechInput):
    # print("#" * 5, input_data.dict())

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = input_data.json()
    headers = {
        'xi-api-key': ELEVENLABS_API_KEY,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for HTTP error status codes
        audio_data = response.content  # Get the binary audio data
        return Response(content=audio_data, media_type='audio/mpeg')  # Return audio data as Response
    except requests.exceptions.RequestException as e:
        return str(e)
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

    