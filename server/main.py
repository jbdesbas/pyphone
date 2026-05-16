from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from dotenv import load_dotenv
import random
from os import getenv
from datetime import datetime
from zoneinfo import ZoneInfo
import wave
from piper import PiperVoice



load_dotenv()

BASE_DIR = Path(getenv("BASE_DIR"))

app = FastAPI()

#model_name = "fr_FR-gilles-low.onnx"
model_name = "fr_FR-mls-medium.onnx"

voice = PiperVoice.load("synth_models/"+model_name)
tz = ZoneInfo("Europe/Paris")


@app.get("/sound/{folder}.wav")
@app.get("/sound/{folder}")
def random_music(folder: str):
    """
    Retourne un fichier audio WAV aléatoire dans un dossier donné.

    - folder: nom du dossier (ex: 04, 05)
    - retourne: fichier WAV streamé
    """

    if folder.endswith(".wav"):
        folder = folder[:-4]

        
    if folder == '01':
        outfile = generate_voice()
    else:
        outfile = get_random_file(folder)
        
    return FileResponse(
        outfile,
        media_type="audio/wav"
    )


    
    
def generate_voice():
    now = datetime.now(tz)

    hour = now.hour
    minute = now.minute

    with wave.open("synth.wav", "wb") as wav_file: # TODO convertire en wav 8khz
        voice.synthesize_wav(f"Il est {hour} heures {minute}. C'est bientôt l'heure de se coucher pour Lily et Garance!", wav_file)
    
    return "synth.wav"  
  
def get_random_file(folder):
    target = BASE_DIR / folder
    if not target.exists() or not target.is_dir():
        raise HTTPException(status_code=404)

    files = list(target.glob("*.wav"))

    if not files:
        raise HTTPException(status_code=404)

    selected = random.choice(files)
    
    return selected

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True
    )
