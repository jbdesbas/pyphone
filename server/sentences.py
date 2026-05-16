import random
from datetime import datetime, time, date
from zoneinfo import ZoneInfo

tz = ZoneInfo("Europe/Paris")

def sentence_now():
    """ Générer une phrase automatiquement en fonction de la date et l'heure """
    now = datetime.now(tz)

    hour = now.hour
    minute = now.minute
    
    choice = random.choice(["heure", "date_remaning"])
    
    if choice == "heure" :
        if now.time() >= time(19,30) and now.time() < time(20,30) :
            comment = "C'est bientôt l'heure de se coucher pour Lily et Garance."
        elif now.time() >= time(20,30)  or now.time() < time(4,0) :
            comment = "Lily et Garance devrai déjà être couché."
        
        return f"Il est {hour} heures {minute}. {comment}"
        
    elif choice == "date_remaning":
        until = (date(2026, 12, 25) - now.date()).days
        
        return f"Plus que {until} jours avant Noël."
