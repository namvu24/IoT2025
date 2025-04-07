from machine import Pin
import time

button = Pin(15, Pin.IN, Pin.PULL_UP)

press_count = 0

previous_state = 1  

while True:
    
    current_state = button.value()

 
    if previous_state == 1 and current_state == 0:
        press_count += 1  
        print("Button pressed, count:", press_count)

    
    previous_state = current_state

    time.sleep(0.1)  
