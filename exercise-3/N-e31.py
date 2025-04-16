from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import dht
import time

# INIT CONSTANTS
WIDTH = 128
HEIGHT = 64

# INIT COMPONENTS
i2c = I2C(0,scl=Pin(17),sda=Pin(16),freq=200000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
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
    print("Temperature:{}, Humidity:{}".format(temperature, humidity))
    oled.fill(0)
    oled.text(f"Temperature:{temperature}", 0, 0)
    oled.text(f"Humidity:{humidity}", 0, 10)
    oled.show()

while True:
    read_sensor()
    time.sleep(1)
