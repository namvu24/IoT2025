from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time

WIDTH = 128
HEIGHT = 64

i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=200000)

oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

button = Pin(18, Pin.IN, Pin.PULL_UP)

max_lines = HEIGHT // 8  
messages = []

def draw_messages():
    oled.fill(0)  
    for i, msg in enumerate(messages[-max_lines:]):
        oled.text(msg, 0, i * 8)
    oled.show()

def check_button():
    if not button.value(): 
        global messages
        messages = []
        draw_messages()

def main():
    try:
        while True:
            check_button()
            user_input = input("Enter message: ")
            messages.append(user_input)
            draw_messages()
    except KeyboardInterrupt:
        print("Exiting...")

main()
