import time
import analogio
import digitalio
import board
import math
import usb_hid
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

#INITIALIZE MOUSE
mouse = Mouse(usb_hid.devices)

#INITIALIZE KEYBOARD

keyboard = Keyboard(usb_hid.devices)

#PIN SETUP
potentiometer = analogio.AnalogIn(board.GP26)

sck = digitalio.DigitalInOut(board.GP14)
sck.direction = digitalio.Direction.OUTPUT

out = digitalio.DigitalInOut(board.GP15)
out.direction = digitalio.Direction.INPUT

#SLIDE POT SETUP
def get_potentiomer_value():
    return(int(potentiometer.value * 100) // 65536)

last_value = get_potentiomer_value()

#BUTTON SETUP
button = digitalio.DigitalInOut(board.GP16)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

#ADC SETUP
MAX_ADC_VALUE = (1 << 24) - 1 #16,777,215

#PRESSURE SENSOR SETUP
def read_adc():
    result = 0

    for i in range(25):
        sck.value = True
        time.sleep(0.001)
        sck.value = False
        time.sleep(0.001)
        result = (result << 1) | out.value
    return result

spacebar_held = False

#DEBOUNCE PARAMETERS
debounce_delay = 0.01
last_button_state = True
last_debounce_time = time.monotonic()

while True:

    #READ BUTTON STATE
    current_button_state = button.value

    if current_button_state != last_button_state:
        last_debounce_time = time.monotonic()

    if(time.monotonic() - last_debounce_time) > debounce_delay:

        if current_button_state == False:
            if not spacebar_held:
                keyboard.press(Keycode.SPACE)
                spacebar_held = True
        else:
            if spacebar_held:
                keyboard.release(Keycode.SPACE)
                spacebar_held = False
    last_button_state = current_button_state

    #CHECK POT VALUE
    current_value = get_potentiomer_value()

    #MOVEMENT COMPARISON
    movement = current_value - last_value

    #MOVE MOUSE
    if abs(movement) >2:
        mouse.move(y=movement * 20)
        last_value = current_value

    #BREATH INPUT

    adc_value = read_adc()
    print("Raw ADC Value:", adc_value)


    time.sleep(0.001)
