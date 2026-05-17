import random
from datetime import datetime, time, date
from zoneinfo import ZoneInfo
import locale
import requests

locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

tz = ZoneInfo("Europe/Paris")

def now():
    return datetime.now(tz)


def weather():
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": 49.89,
        "longitude": 2.30,
        "current_weather": True
    }

    return requests.get(url, params=params).json()

def temperature():
    return weather().get('current_weather').get('temperature')

class Sentence:
    def __init__(self, text_func, condition_func=lambda: True):
        self.text_func = text_func
        self.condition_func = condition_func

    def text(self):
        return self.text_func()

    def is_active(self):
        return self.condition_func()
    

class SentenceChooser:
    def __init__(self):
        self.sentences = []

    def add(self, sentence: Sentence):
        self.sentences.append(sentence)

    def available_sentences(self):
        return [
            sentence
            for sentence in self.sentences
            if sentence.is_active()
        ]

    def choose(self):
        available = self.available_sentences()

        if not available:
            return None

        selected = random.choice(available)

        return selected.text()


chooser = SentenceChooser()

# --------------------------------------------------
# Custom sentences
# --------------------------------------------------
my_sentences = [
Sentence(
    lambda: f"déja {now().hour} heure {now().minute}. c'est biento l'heure de se coucher pour lily et garance.",
    lambda: time(19, 30) <= now().time() < time(20, 30)
),
Sentence(
    lambda: f"il est {now().hour} heure {now().minute}. garance et lily devrai déjà être couché.",
    lambda: time(20, 30) <= now().time() < time(4, 0)
),
Sentence(
    lambda: f"il est {now().hour} heure {now().minute}. Passé une bonne apré midi.",
    lambda: time(13, 0) <= now().time() < time(16, 0)
),
Sentence(
    lambda: f"avé vous pri le gouté ?",
    lambda: time(16,0) <= now().time() < time(17,0)
),
Sentence(
    lambda: f"plus que {(date(2026, 12, 25) - now().date()).days} jours avant noel.",
    lambda: True
),
Sentence(
    lambda: f"c'est le weekend ! je suis content. et toi ? ",
    lambda: now().weekday() >= 5
),
Sentence(
    lambda: f"aujourdui, nous somme {now().strftime('%A')}.",
    lambda: True
),
Sentence(
    lambda: f"c'est {now().strftime('%A')}, passé une bonne journé.",
    lambda: time(6, 30) <= now().time() < time(8, 30)
),
Sentence(
    lambda: (
        lambda t: (
            f"dehor il fai {round(t)} degré. "
            + ("c'est glacial." if t < 0 else "pensé a mettre un pule" if t < 18 else "c'est agréable.")
        )
    )(temperature()),
    lambda: True
),
]

for s in my_sentences:
    chooser.add(s)
