from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from typing import AsyncIterator
from pathlib import Path
from dotenv import load_dotenv
import random
from os import getenv
import wave
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from piper import PiperVoice
import numpy as np
from fastapi_cache.decorator import cache
from sentences import chooser

load_dotenv()

BASE_DIR = Path(getenv("BASE_DIR"))
SAMPLE_RATE = 8e3


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    FastAPICache.init(InMemoryBackend())
    yield


app = FastAPI(lifespan=lifespan)

model_name = "fr_FR-gilles-low.onnx"
#model_name = "fr_FR-mls-medium.onnx"

voice = PiperVoice.load("synth_models/"+model_name)

sentence_chooser = chooser


@cache(expire=1)
async def cached_generate_voice():
    return generate_voice()


@app.get("/sound/{folder}.wav")
@app.get("/sound/{folder}")
async def random_music(folder: str):
    """
    Retourne un fichier audio WAV aléatoire dans un dossier donné.

    - folder: nom du dossier (ex: 04, 05)
    - retourne: fichier WAV streamé
    """

    if folder.endswith(".wav"):
        folder = folder[:-4]

        
    if folder == '01':
        outfile = await cached_generate_voice()
    else:
        outfile = get_random_file(folder)
        
    return FileResponse(
        outfile,
        media_type="audio/wav"
    )

@app.get("/test")
def test():
    return FileResponse(
        "ready.wav",
        media_type="audio/wav"
    )

def generate_voice():
    text = sentence_chooser.choose()
    print("say: ", text)
    with wave.open("synth.wav", "wb") as wf:
        voice.synthesize_wav(text, wf)
  
    outfile = process_file("synth.wav", sample_rate=SAMPLE_RATE)
    #return "synth.wav"
    return outfile  
  
def get_random_file(folder):
    target = BASE_DIR / folder
    if not target.exists() or not target.is_dir():
        raise HTTPException(status_code=404)

    files = list(target.glob("*.wav"))

    if not files:
        raise HTTPException(status_code=404)

    selected = random.choice(files)
    
    return selected


    
    
def process_file(input_file, sample_rate=8e3): # Préparer un fichier pour stream sur ESP32
    output = "ready.wav"
    
    def resample(pcm_bytes: bytes, src_rate: int, dst_rate: int, sampwidth: int) -> bytes:
        """ IA Generated """
        dtype = np.int16 if sampwidth == 2 else np.int8
        samples = np.frombuffer(pcm_bytes, dtype=dtype)
        num_out = int(len(samples) * dst_rate / src_rate)
        resampled = np.interp(
            np.linspace(0, len(samples), num_out),
            np.arange(len(samples)),
            samples
        ).astype(dtype)
        
        return resampled.tobytes()

    #RE-ECRIRE le fichier à 8KHZ
    with wave.open(input_file, "rb") as wf:
        src_rate = wf.getframerate()
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        pcm_data = wf.readframes(wf.getnframes())

    pcm_resampled = resample(pcm_data, src_rate, sample_rate, sampwidth)

    # Réécrire un WAV propre à 8000 Hz
    with wave.open(output, "wb") as wf:
        wf.setnchannels(n_channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_resampled)
    
    return output
    
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True,
        workers=1
    )
