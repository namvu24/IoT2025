from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
WIDTH =128
HEIGHT= 64
#Create the I2C connection
i2c=I2C(0,scl=Pin(17),sda=Pin(16),freq=200000)
#Initialize the OLED display
oled = SSD1306_I2C(WIDTH,HEIGHT,i2c)
#Update the frame buffer with some text
oled.text("Hello World", 0, 0)
#Draw the frame on the display
oled.show()