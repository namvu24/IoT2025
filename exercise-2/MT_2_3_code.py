from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time
import random

WIDTH = 128
HEIGHT = 64

i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=200000)

oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

button = Pin(15, Pin.IN, Pin.PULL_UP)

dice_faces = {
    1: [(64, 32)],
    2: [(48, 32), (80, 32)],
    3: [(48, 24), (64, 32), (80, 40)],
    4: [(48, 24), (48, 40), (80, 24), (80, 40)],
    5: [(48, 24), (48, 40), (64, 32), (80, 24), (80, 40)],
    6: [(48, 24), (48, 32), (48, 40), (80, 24), (80, 32), (80, 40)]
}

def draw_dice(number):
    oled.fill(0)  
    for x, y in dice_faces[number]:
        oled.fill_rect(x, y, 6, 6, 1)  
    oled.show()

def wait_for_button_press():
    while button.value():  
        pass
    time.sleep(0.2)  
    while not button.value():  
        pass
    time.sleep(0.2)  

def main():
    try:
        while True:
            wait_for_button_press()
            dice_number = random.randint(1, 6)
            draw_dice(dice_number)
    except KeyboardInterrupt:
        print("Exiting...")

main()
