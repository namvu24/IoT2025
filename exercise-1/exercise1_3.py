from machine import Pin
import time
import random  


button = Pin(15, Pin.IN, Pin.PULL_UP)


button_was_pressed = False

while True:
    if button.value() == 0 and not button_was_pressed:
        
        roll = random.randint(1, 6)  
        print(f"You rolled a {roll}")
        button_was_pressed = True

    elif button.value() == 1 and button_was_pressed:
        
        button_was_pressed = False

    time.sleep(0.05)  
