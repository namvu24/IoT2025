from machine import Pin
import random
import time
button = Pin(15, Pin.IN, Pin.PULL_UP)
s = 1 # the status of the button
while True:
    if button.value() != s:
        s = button.value()
        if s == 0:
            print(random.randint(1, 6))
    time.sleep(0.1)