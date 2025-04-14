from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf
import time
import select
import sys

WIDTH =128
HEIGHT= 64
messages = []

#Create the I2C connection
i2c=I2C(0,scl=Pin(17),sda=Pin(16),freq=200000)
#Initialize the OLED display
display = SSD1306_I2C(WIDTH,HEIGHT,i2c)
#Update the frame buffer with some text
fbuf = framebuf.FrameBuffer(bytearray(WIDTH * HEIGHT * 1), WIDTH, HEIGHT, framebuf.MONO_VLSB)
# the button
button = Pin(15, Pin.IN, Pin.PULL_UP)
previous_button_state = 1 # the status of the button

def get_input():
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.readline().strip()
    return None

while True:
    user_input = get_input()
    if user_input:
        messages.append(user_input)
        if len(messages) > 8:
           messages.pop(0)
           
    if button.value() != previous_button_state:
        previous_button_state = button.value()
        if previous_button_state == 0:
            messages = []
    
    display.fill(0)
    y = 0
    for i in messages:
        fbuf.fill(0)
        fbuf.text(i, 0, 0)
        display.blit(fbuf, 0, y, 0)
        y += 8
    display.show()
