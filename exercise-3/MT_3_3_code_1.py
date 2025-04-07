from machine import Pin, ADC, I2C
from ssd1306 import SSD1306_I2C
import dht
import time

# Constants
ADC_RESOLUTION = 65535
VREF = 3.3 
TEMP_SENSOR_ADC = 4 

WIDTH = 128
HEIGHT = 64

i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=200000)

oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

data_pin = Pin(13, Pin.IN, Pin.PULL_UP)
sensor = dht.DHT22(data_pin)

temp_values = []
MAX_SAMPLES = 5

def read_temperature():
    adc = ADC(TEMP_SENSOR_ADC)
    adc_value = adc.read_u16()
    voltage = (adc_value / ADC_RESOLUTION) * VREF
    temperature = 27 - ((voltage - 0.706) / 0.001721)
    return temperature

def update_temperature_list(new_temp):
    if len(temp_values) >= MAX_SAMPLES:
        temp_values.pop(0)
    temp_values.append(new_temp)

def calculate_floating_avg():
    if len(temp_values) == 0:
        return 0
    return sum(temp_values) / len(temp_values)

def display_temperature(avg_temp):
    oled.fill(0) 
    oled.text("Avg Temp: {:.2f}C".format(avg_temp), 0, 20)
    oled.show()

while True:
    current_temp = read_temperature()
    update_temperature_list(current_temp)
    avg_temp = calculate_floating_avg()
    display_temperature(avg_temp)
    time.sleep(1)
