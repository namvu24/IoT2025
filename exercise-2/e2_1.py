from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf
import time

WIDTH =128
HEIGHT= 64
name = "My Name"
name_width = len(name) * 8
name_height = 8
name_x = int((WIDTH - name_width) / 2)
name_y = int((HEIGHT - name_height) / 2)

#Create the I2C connection
i2c=I2C(0,scl=Pin(17),sda=Pin(16),freq=200000)
#Initialize the OLED display
display = SSD1306_I2C(WIDTH,HEIGHT,i2c)
#Update the frame buffer with some text
# fbuf = framebuf.FrameBuffer(bytearray(WIDTH * HEIGHT * 1), WIDTH, HEIGHT, framebuf.MONO_VLSB)
show_text = True

button = Pin(15, Pin.IN, Pin.PULL_UP)
previous_button_state = 1 # the status of the button
while True:
    if button.value() != previous_button_state:
        previous_button_state = button.value()
        if previous_button_state == 0 and show_text:
            display.fill(0)
            display.text(name, name_x, name_y)
            display.show()
            show_text = False
        elif previous_button_state == 0 and not show_text:
            display.fill(0)
            display.show()
            show_text = True
        time.sleep(0.1)
