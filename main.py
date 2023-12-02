import network
from machine import RTC, I2C, Pin, unique_id, reset
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

mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode() #client id ?
client_id = mac
print('MAC :', mac)

df=DFPlayer(uart_id=1) # D4

hangup_pin = Pin(5,Pin.IN, Pin.PULL_UP) # D1
rotary1_pin = Pin(14, Pin.IN, Pin.PULL_UP) # D5
rotary2_pin = Pin(12, Pin.IN, Pin.PULL_UP) # D6

previous_state = False

# Adapt for your folders
folders_n_tracks = [  # Numbers of tracks in each folder (can't find a "play random in tracks" function for RDFPlayer)
None, # 0 (unused)
7, # 01
11,
3, # 03
6,
3, # 05
2,
3, # 07
0,
8,
13 # 10 (messages)
]

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

while True :
    #do_connect(WIFI_SSID, WIFI_PASSWORD)      

    is_off_hook = hangup_pin.value() == 0
    toggle = is_off_hook != previous_state
    if is_off_hook and toggle:
        print('Pick Up!') 
        df.send_cmd(0x17,0x00, 99) # Loop folder 99. CF https://cahamo.delphidabbler.com/resources/dfplayer-mini
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
            utime.sleep_ms(2000)
        df.play(rotary_value, randint_between(1,folders_n_tracks[rotary_value]))
    utime.sleep_ms(250)

