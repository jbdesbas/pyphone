import requests
import xml.etree.ElementTree as ET
from pydub import AudioSegment

class LesDentsEtDodo(object):
    def __init__(self):
        self.feedUrl = "https://feeds.simplecast.com/Y_A8bQt7"
        pass

    def getIndex(self):
        r = requests.get(self.feedUrl)
        return r.text
    

    def get_first_mp3_url(self) -> str | None:

        xml = self.getIndex()
        root = ET.fromstring(xml)

        # Cherche la première balise <enclosure>
        enclosure = root.find(".//enclosure")

        if enclosure is not None:
            return enclosure.get("url")

        return None
    
    def getFile(self, output):
        response = requests.get(self.get_first_mp3_url())
    
        with open('temp.mp3', 'wb') as f:
            f.write(response.content)

        audio = AudioSegment.from_file('temp.mp3', format="mp3")
        
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(8000)
        extract = audio[26.5*1e3:] - 8 # cut 26 first secondes, reduce volume
        extract.export(output, format="wav")



def convert_mp3_url_to_wav(url: str, output_path: str):
    response = requests.get(url)
    
    with open('temp.mp3', 'wb') as f:
        f.write(response.content)

    audio = AudioSegment.from_file('temp.mp3', format="mp3")
    
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(8000)
    
    audio.export(output_path, format="wav")
