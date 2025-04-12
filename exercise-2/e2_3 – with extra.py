# THIS ONE WITH EXTRA FUNCTION: YOU CAN ADJUST THE SIZE OF THE DICE BY PRESSING THE BUTTON MORE THAN 3 S

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
button_pressed_time = 0
adjust_size = False
dice_number = 0


while True:
    if button.value() != previous_button_state or adjust_size == True:
        previous_button_state = button.value()
        if button.value() == 0:
            if adjust_size == False:
                button_pressed_time = time.ticks_ms()
                dice_number = random.randint(0, 5)
            display.fill(0)
            fbuf.fill(0)
            fbuf.rect(rect_x, rect_y, rect_size, rect_size, 1)
            for i in dice[dice_number]:
                fbuf.ellipse(int(rect_x + i[0]/4*rect_size), int(rect_y + i[1]/4*rect_size), circle_radius, circle_radius, 1, True)
            display.blit(fbuf, 0, 0, 0)
            display.show()
    if (time.ticks_ms() - button_pressed_time) > 3000 and button_pressed_time != 0 and button.value() == 0:
        adjust_size = True
        rect_size += 1
        if rect_size > 70:
            rect_size = 5
        rect_x = int((WIDTH - rect_size) / 2)
        rect_y = int((HEIGHT - rect_size) / 2)
        circle_radius = int(1/12*rect_size)
        time.sleep(0.05)
    if adjust_size == True and button.value() == 1:
        adjust_size = False
        button_pressed_time = time.ticks_ms()