from machine import Pin
import time
button = Pin(15, Pin.IN, Pin.PULL_UP)
s = 1 # the status of the button
p = 0 # variable that counts the button presses
while True:
    if button.value() != s:
        s = button.value()
        if s == 0:
            p += 1
            print("Button was pressed " + str(p) + " times")
    time.sleep(0.1)