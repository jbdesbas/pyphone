from sentences import now
from stream import LesDentsEtDodo, convert_mp3_url_to_wav

#devnote : pour l'info du jour, utiliser : https://api.playbacpresse.fr/articles?newspaper=lepq&limit=5 ?

def handle_menu(state: str, key: str | None = None):

    if state is None:
        return dict(state="main", sentence=f""" il est {now().hour} heure {now().minute}. 
                    Pour la météo, tapé 1. Pour l'information du jour, tapé 2.""")
    if state == "main":
        if int(key) == 1:
            return dict(state="weather", sentence="""Voici la météo.""")
        if int(key) == 2:
            podcast = LesDentsEtDodo()
            buffer = podcast.getBuffer()
            return dict(state="podcast", audio_file=buffer)
