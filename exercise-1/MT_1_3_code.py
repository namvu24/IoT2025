from machine import Pin
import random
import time


button = Pin(15, Pin.IN, Pin.PULL_UP)


previous_state = 1  

while True:
    
    current_state = button.value()

    
    if previous_state == 1 and current_state == 0:
        
        dice_roll = random.randint(1, 6)
        print("You rolled a:", dice_roll)

    
    previous_state = current_state

    time.sleep(0.1)
