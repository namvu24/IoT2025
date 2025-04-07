from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import dht
import time

WIDTH = 128
HEIGHT = 64

i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=200000)

oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

data_pin = Pin(13, Pin.IN, Pin.PULL_UP)
sensor = dht.DHT22(data_pin)

def read_sensor():
    try:
        sensor.measure()
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        display_sensor_data(temperature, humidity)
    except OSError:
        oled.fill(0)
        oled.text("Sensor Error", 20, 20)
        oled.show()

def display_sensor_data(temperature, humidity):
    oled.fill(0)
    oled.text("Temperature: {:.1f}C".format(temperature), 0, 10)
    oled.text("Humidity: {:.1f}%".format(humidity), 0, 30)
    oled.show()

while True:
    read_sensor()
    time.sleep(1)