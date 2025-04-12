from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import random
import time
import framebuf

WIDTH = 128
HEIGHT = 64
rect_size = 60
rect_x = int((WIDTH - rect_size) / 2)
rect_y = int((HEIGHT - rect_size) / 2)
circle_radius = int(1/12*rect_size)
dice = [ [[2,2]], [[1,2],[3,2]], [[1,1],[2,2],[3,3]], [[1,1],[3,1],[1,3],[3,3]], [[1,1],[3,1],[2,2],[1,3],[3,3]], [[1,1],[3,1],[1,2],[3,2],[1,3],[3,3]] ]

#Create the I2C connection
i2c=I2C(0,scl=Pin(17),sda=Pin(16),freq=200000)
#Initialize the OLED display
display = SSD1306_I2C(WIDTH,HEIGHT,i2c)
fbuf = framebuf.FrameBuffer(bytearray(WIDTH * HEIGHT * 1), WIDTH, HEIGHT, framebuf.MONO_VLSB)
button = Pin(15, Pin.IN, Pin.PULL_UP)
previous_button_state = 1 # the status of the button


while True:
    if button.value() != previous_button_state:
        previous_button_state = button.value()
        if button.value() == 0:
            display.fill(0)
            fbuf.fill(0)
            fbuf.rect(rect_x, rect_y, rect_size, rect_size, 1)
            for i in dice[random.randint(0, 5)]:
                fbuf.ellipse(int(rect_x + i[0]/4*rect_size), int(rect_y + i[1]/4*rect_size), circle_radius, circle_radius, 1, True)
            display.blit(fbuf, 0, 0, 0)
            display.show()
