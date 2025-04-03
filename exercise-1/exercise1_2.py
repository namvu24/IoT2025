from machine import Pin
import time

button = Pin(15, Pin.IN, Pin.PULL_UP)

press_count = 0
button_was_pressed = False


while True:
    if button.value() == 0 and not button_was_pressed:
        press_count += 1
        print(f"Button was pressed {press_count} times")
        button_was_pressed = True
    elif button.value() == 1 and button_was_pressed:
        button_was_pressed = False
        
    time.sleep(0.05)