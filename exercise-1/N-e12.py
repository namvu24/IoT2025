from machine import Pin
import time

# INIT COMPONENTS
button = Pin(15, Pin.IN, Pin.PULL_UP)
led = Pin("LED", Pin.OUT)

# INIT CONSTANTS
BUTTON_PRESSED_STATE = 0
BUTTON_RELEASED_STATE = 1

# DEFINE FUNCTIONS
def main():
    # set initial previous button state to released
    prev_button_state = BUTTON_RELEASED_STATE
    count = 0
    led.off()

    while True:
        button_state = button.value()
        
        # do task if button is pressed and prev state must not be the same as current state
        if prev_button_state != button_state and button_state == BUTTON_PRESSED_STATE:
            count += 1
            led.on()
            print(f"The button is pressed {count} times.")
        
        # do task if button is release and prev state must not be the same as current state
        if prev_button_state != button_state and button_state == BUTTON_RELEASED_STATE:
            led.off()

        # set prev button state as button state for next time
        prev_button_state = button_state
    
# START MAIN
main()
        
