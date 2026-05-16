from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from dotenv import load_dotenv
import random
from os import getenv

load_dotenv()

BASE_DIR = Path(getenv("BASE_DIR"))

app = FastAPI()


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
    target = BASE_DIR / folder
    print(folder, target)
    if not target.exists() or not target.is_dir():
        raise HTTPException(status_code=404)

    files = list(target.glob("*.wav"))

    if not files:
        raise HTTPException(status_code=404)

    selected = random.choice(files)

    return FileResponse(
        selected,
        media_type="audio/wav",
        filename=selected.name
    )
    
    
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True
    )
