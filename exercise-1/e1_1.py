from machine import Pin
import time

led = Pin("LED", Pin.OUT)

x = [[.5, .5], [.5, .5], [.5, 1.5], [1.5, .5], [1.5, .5], [1.5, 1.5], [.5, .5], [.5, .5], [.5, 3.5]]

while True:
    for i in x:
        led.on()
        time.sleep(i[0])
        led.off()
        time.sleep(i[1])