from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time

# INIT COMPONENTS
button = Pin(15, Pin.IN, Pin.PULL_UP)
led = Pin("LED", Pin.OUT)
i2c=I2C(0,scl=Pin(17),sda=Pin(16),freq=200000)

# INIT CONSTANTS
BUTTON_PRESSED_STATE = 0
BUTTON_RELEASED_STATE = 1
WIDTH = 128
HEIGHT = 64

#Initialize the OLED display
oled = SSD1306_I2C(WIDTH,HEIGHT,i2c)

#


# DEFINE FUNCTIONS
def button_pressed(prev_button_state):
    screen_on = 0
    button_state = button.value()

    # do task if button is pressed and prev state must not be the same as current state
    if prev_button_state != button_state and button_state == BUTTON_PRESSED_STATE:
        led.on()
        print("button pressed")
        if screen_on == 0:
            screen_on = 1
            oled.text("Hello World", 0, int(HEIGHT/2))
            oled.show()
        else:
            screen_on = 0
            oled.fill(0)
            oled.show()
    
    # do task if button is release and prev state must not be the same as current state
    if prev_button_state != button_state and button_state == BUTTON_RELEASED_STATE:
        led.off()

    # set prev button state as button state for next time
    prev_button_state = button_state
    return prev_button_state

def main():
    prev_button_state = BUTTON_RELEASED_STATE
    while True:
        prev_button_state = button_pressed(prev_button_state)
        time.sleep_ms(100)
    
# START MAIN
main()