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

rtc = RTC()

mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode() #client id ?
client_id = mac
print('MAC :', mac)

df=DFPlayer(uart_id=1) # D4

hangup_pin=Pin(5,Pin.IN, Pin.PULL_UP) # D1


previous_state = False

while True :
    #do_connect(WIFI_SSID, WIFI_PASSWORD)      

    is_off_hook = hangup_pin.value() == 0
    toggle = is_off_hook != previous_state
    if is_off_hook and toggle:
        print('Pick Up!') # Ajouter un delay ?
        df.play(1,1)
    elif not is_off_hook and toggle:
        print('Hang Up..')
        df.stop()
    #print(is_off_hook)
    previous_state = is_off_hook
    utime.sleep_ms(250)

