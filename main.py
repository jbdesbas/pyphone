import network
from machine import RTC, I2C, Pin, unique_id, reset, WDT
from config import *
import ubinascii
import utime
import ntptime
from lib.dfplayer import DFPlayer
from random import getrandbits

CONFIG={}

def do_connect(ssid,pwd):
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, pwd)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())



wlan = network.WLAN(network.STA_IF)
wlan.active(False) # No wifi needed

rtc = RTC()

wdt = WDT() # Init watchdog timer. On ESP8266 timeout is

mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode() #client id ?
client_id = mac
print('MAC :', mac)

df=DFPlayer(uart_id=1) # D4
df.volume(26)


hangup_pin = Pin(5,Pin.IN, Pin.PULL_UP) # D1
busy_pin = Pin(4, Pin.IN, Pin.PULL_UP) # D2
rotary1_pin = Pin(14, Pin.IN, Pin.PULL_UP) # D5
rotary2_pin = Pin(12, Pin.IN, Pin.PULL_UP) # D6

previous_state = False

# Adapt for your folders
folders_n_tracks = [  # Numbers of tracks in each folder (can't find a "play random in tracks" function for RDFPlayer)
None, # 0 (unused)
8, # 01
13,
6, # 03
7,
4, # 05
3,
3, # 07
6,
8,
13 # 10 (messages)
]

available_tracks = []
for e in folders_n_tracks : # Random play in folder, but don't play twice same tracks
    if e or 0 > 0 :
        available_tracks.append(list(range(1, e+1)))
    else :
        available_tracks.append(list())
 

def all_played_in_folder(folder):
    available_tracks[folder] = list(range(1, folders_n_tracks[folder]+1))

def rotary():
    i = 0
    previous_value = None
    while True:
        if rotary1_pin.value() == 0:
            value = rotary2_pin.value()
            if value == 1 and previous_value != value:
                i+=1
            previous_value = value
            utime.sleep_ms(10)
            wdt.feed()
        else:
            return None if i == 0 else i

def randint_between(a, b):
    if a > b:
        raise ValueError("La valeur de 'a' doit être inférieure ou égale à 'b'")
    num_values = b - a + 1
    if num_values <= 0:
        raise ValueError("La plage [a, b] est invalide")
    num_bits = 0
    while (1 << num_bits) < num_values:
        num_bits += 1
    random_bits = getrandbits(num_bits)
    while random_bits >= num_values:
        random_bits = getrandbits(num_bits)
    result = random_bits + a
    return result

idle_tick = 0
while True :
    is_off_hook = hangup_pin.value() == 0
    is_idle = busy_pin.value() == 1
    toggle = is_off_hook != previous_state

    if is_idle and is_off_hook :
        idle_tick+=1
    else:
        idle_tick = 0

    if is_off_hook and toggle:
        print('Pick Up!') 
        df.send_cmd(0x17,0x00, 99) # Loop folder 99. CF https://cahamo.delphidabbler.com/resources/dfplayer-mini
    elif is_off_hook and idle_tick > 3 :
        print('Tuuuut...')
        df.send_cmd(0x17,0x00, 99) # Loop folder 99.
        utime.sleep_ms(100)
    elif not is_off_hook and toggle:
        print('Hang Up..')
        df.stop()
    #print(is_off_hook)
    previous_state = is_off_hook
    rotary_value = rotary()
    if rotary_value :
        print(rotary_value)
        if rotary_value == 10:
            df.play(98,1) # Vous avez un nouveau message
            for t in range(0,10) : # sleep for 2 seconds (200*10) ("vous avez un message" duration)
                utime.sleep_ms(200)
                wdt.feed()
        n_track = available_tracks[rotary_value][ randint_between(1,len(available_tracks[rotary_value]))-1 ]
        available_tracks[rotary_value].remove(n_track)
        if len(available_tracks[rotary_value]) == 0:
            all_played_in_folder(rotary_value) # reset folder
        df.play(rotary_value, n_track ) # Play random song not already played
    wdt.feed()
    utime.sleep_ms(250)

