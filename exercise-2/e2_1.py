from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf
import time

WIDTH =128
HEIGHT= 64
name = "Eelis Kuisma"
name_width = len(name) * 8
name_height = 8
name_x = int((WIDTH - name_width) / 2)
name_y = int((HEIGHT - name_height) / 2)

#Create the I2C connection
i2c=I2C(0,scl=Pin(17),sda=Pin(16),freq=200000)
#Initialize the OLED display
display = SSD1306_I2C(WIDTH,HEIGHT,i2c)
#Update the frame buffer with some text
fbuf = framebuf.FrameBuffer(bytearray(WIDTH * HEIGHT * 1), WIDTH, HEIGHT, framebuf.MONO_VLSB)

button = Pin(15, Pin.IN, Pin.PULL_UP)
s = 1 # the status of the button
while True:
    if button.value() != s:
        s = button.value()
        if s == 0:
            display.fill(0)
            fbuf.text(name, name_x, name_y)
            display.blit(fbuf, 0, 0, 0)
            display.show()
    time.sleep(0.1)