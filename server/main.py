import io
from os import getenv
import random
from pathlib import Path

import wave
from dotenv import load_dotenv
from pydub import AudioSegment
from fast_cache import cache, InMemoryBackend
from piper import PiperVoice

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from sentences import chooser
from menu import handle_menu


load_dotenv()

BASE_DIR = Path(getenv("BASE_DIR"))
SAMPLE_RATE = 8_000




app = FastAPI()

backend = InMemoryBackend()
cache.init_app(app, backend)

model_name = "fr_FR-gilles-low.onnx"
#model_name = "fr_FR-mls-medium.onnx"

voice = PiperVoice.load("synth_models/"+model_name)

sentence_chooser = chooser


sessions = {} # mono worker only


@app.get("/sound/{folder}.wav")
@app.get("/sound/{folder}")
@cache.cached(expire=3)
def random_music(folder: str, device_key: str):
    """
    Retourne un fichier audio WAV aléatoire dans un dossier donné.

    - folder: nom du dossier (ex: 04, 05)
    - retourne: fichier WAV streamé
    """

    if folder.endswith(".wav"):
        folder = folder[:-4]

    session = sessions.get(device_key)
    state = session.get("state") if session else None
    if folder == '01' or state is not None :
        #outfile = generate_voice()  # random sentence
        
        menu = handle_menu(state, folder)
        buffer = generate_voice(menu.get("sentence")) if menu.get("sentence") else menu.get('audio_file')
        sessions.setdefault(
            device_key,
            {"state": menu.get("state")}
        )
    else:
        buffer = get_random_file('00' if folder=="10" else folder)
    return StreamingResponse(
        buffer,
        media_type="audio/wav"
    )


# Raccroche le téléphone
@app.get("/hangup")
def hangup(device_key: str):
    sessions.pop(device_key, None)
    return {"ok": True}


# Décroche le téléphone
@app.get("/pickup")
def pickup():
    return {"ok": True}


def generate_voice(text: str | None = None):  
    if text is not None:
        sentence = text
    else:
        sentence = sentence_chooser.choose()
    
    print("say: ", sentence)

    buffer = io.BytesIO()
    
    with wave.open(buffer, "wb") as wf:
        voice.synthesize_wav(sentence, wf)

    audio = AudioSegment.from_wav(buffer)
    audio = audio.set_channels(1)       # Mono
    audio = audio.set_frame_rate(SAMPLE_RATE)  # 8 kHz
    audio += AudioSegment.silent(duration=1000)

    out_buffer = io.BytesIO()
    audio.export(out_buffer, format="wav")
    out_buffer.seek(0)

    return out_buffer  
  
def get_random_file(folder):
    target = BASE_DIR / str(int(folder)).zfill(2)
    if not target.exists() or not target.is_dir():
        raise HTTPException(status_code=404)

    files = list(target.glob("*.wav"))

    if not files:
        raise HTTPException(status_code=404)

    selected = random.choice(files)

    audio = AudioSegment.from_wav(selected)
    buffer = io.BytesIO()
    audio.export(buffer, format="wav")
    # Si besoin, on pourra ajouter ici un traitement pour préparer les fichiers pour l'ESP32
    buffer.seek(0)
    return buffer
    

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True,
        workers=1
    )
