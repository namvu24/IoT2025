from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf
import dht
import machine
import time

ad_pin = machine.ADC(4)

WIDTH =128
HEIGHT= 64
#Create the I2C connection
i2c=I2C(0,scl=Pin(17),sda=Pin(16),freq=200000)
#Initialize the OLED display
display = SSD1306_I2C(WIDTH,HEIGHT,i2c)
#Update the frame buffer with some text
fbuf = framebuf.FrameBuffer(bytearray(WIDTH * HEIGHT * 1), WIDTH, HEIGHT, framebuf.MONO_VLSB)

temperatures = []

def calculate_voltage(ad):
    return (ad / (65536 - 1) * 3.3)

def calculate_temperature(voltage):
    return (27 - (voltage - 0.706) / (1.721/1000) )

def print_sensor_data(temperature):
    display.fill(0)
    fbuf.fill(0)
    fbuf.text("Temp: " + str(round(temperature, 1)), 0, 0)
    display.blit(fbuf, 0, 0, 0)
    display.show()
    
def get_average_temperature():
    return sum(temperatures) / len(temperatures)

while True:
    temperatures.append(calculate_temperature(calculate_voltage(ad_pin.read_u16())))
    if len(temperatures) > 5:
        temperatures.pop(0)
    print_sensor_data(get_average_temperature())
    time.sleep(1)