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

hangup_pin = Pin(5,Pin.IN, Pin.PULL_UP) # D1
rotary1_pin = Pin(14, Pin.IN, Pin.PULL_UP) # D5
rotary2_pin = Pin(12, Pin.IN, Pin.PULL_UP) # D6

previous_state = False

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

while True :
    #do_connect(WIFI_SSID, WIFI_PASSWORD)      

    is_off_hook = hangup_pin.value() == 0
    toggle = is_off_hook != previous_state
    if is_off_hook and toggle:
        print('Pick Up!') 
        df.play(99,1) # Problème pour activer le repeat
    elif not is_off_hook and toggle:
        print('Hang Up..')
        df.stop()
    #print(is_off_hook)
    previous_state = is_off_hook
    rotary_value = rotary()
    if rotary_value :
        print(rotary_value)
        df.play(rotary_value, 1)
    utime.sleep_ms(250)

