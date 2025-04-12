from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf
import dht
import time

WIDTH =128
HEIGHT= 64
messages = []

#Create the I2C connection
i2c=I2C(0,scl=Pin(17),sda=Pin(16),freq=200000)
#Initialize the OLED display
display = SSD1306_I2C(WIDTH,HEIGHT,i2c)
#Update the frame buffer with some text
fbuf = framebuf.FrameBuffer(bytearray(WIDTH * HEIGHT * 1), WIDTH, HEIGHT, framebuf.MONO_VLSB)

data_pin = Pin(13, Pin.IN, Pin.PULL_UP)
sensor = dht.DHT22(data_pin)
def read_sensor():
    try:
        sensor.measure()
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        print_sensor_data(temperature, humidity)
    except OSError as e:
        print("Error reading data from the sensor")

def print_sensor_data(temperature, humidity):
    display.fill(0)
    fbuf.fill(0)
    print("Temperature: {}, Humidity: {}".format(temperature, humidity))
    fbuf.text("Temp: " + str(temperature), 0, 0)
    fbuf.text("Humid: " + str(humidity), 0, 20)
    display.blit(fbuf, 0, 0, 0)
    display.show()

while True:
    read_sensor()
    time.sleep(1)