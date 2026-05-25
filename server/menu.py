from sentences import now, sentence_weather
from stream import LesDentsEtDodo

#devnote : pour l'info du jour, utiliser : https://api.playbacpresse.fr/articles?newspaper=lepq&limit=5 ?




def handle_menu(state: str, key: str | None = None):

    if state is None:
        return dict(state="main", sentence=f""" il est {now().hour} heure {now().minute}. 
                    Pour la météo, tapé 1. Pour l'information du jour, tapé 2.""")
    if state == "main":
        if int(key) == 1:
            return dict(state="weather", sentence=sentence_weather.text())
        if int(key) == 2:
            podcast = LesDentsEtDodo()
            buffer = podcast.getBuffer()
            return dict(state="podcast", audio_file=buffer)
        
    return dict(state="main", sentence=f"Le numéro {int(key)} n'est pas encore disponible.")
