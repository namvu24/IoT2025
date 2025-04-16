from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import dht
import time

# INIT CONSTANTS
WIDTH = 128
HEIGHT = 64
T_LENGTH = 5

# INIT COMPONENTS
i2c = I2C(0,scl=Pin(17),sda=Pin(16),freq=200000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
data_pin = Pin(13, Pin.IN, Pin.PULL_UP)
sensor = dht.DHT22(data_pin)
analog_value = machine.ADC(28)
temp_arr = []
        
def print_sensor_data(temperature):
    print("Temperature:{}".format(temperature))
    oled.fill(0)
    oled.text(f"Temperature:{temperature}", 0, 0)
    oled.show()

def calculate_temperature(voltage):
    return (27 - (voltage-0.706)/1.721)

def calculate_voltage(ad):
    return (ad * 3.3/65535)

while True:
    ad = analog_value.read_u16()
    
    # read sensor and add to array
    if len(temp_arr) == T_LENGTH:
        temp_arr.pop(0)
    temp_arr.append(calculate_temperature(calculate_voltage(ad)))
    
    # calculate avg value
    total = 0
    for x in temp_arr:
       total += x
       
    # print to oled
    print(temp_arr)
    print_sensor_data(total/len(temp_arr))
    time.sleep(1)

