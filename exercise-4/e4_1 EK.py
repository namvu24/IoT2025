import network
from time import sleep
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf
import time

WIDTH =128
HEIGHT= 64

#Create the I2C connection
i2c=I2C(0,scl=Pin(17),sda=Pin(16),freq=200000)
#Initialize the OLED display
display = SSD1306_I2C(WIDTH,HEIGHT,i2c)
#Update the frame buffer with some text
fbuf = framebuf.FrameBuffer(bytearray(WIDTH * HEIGHT * 1), WIDTH, HEIGHT, framebuf.MONO_VLSB)


# Replace these values with your own
SSID = "SmartIoTMQTT"
PASSWORD = "SmartIot"
BROKER_IP = "192.168.1.254"

# Function to connect to WLAN
def connect_wlan():
    # Connecting to the group WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    # Attempt to connect once per second
    while wlan.isconnected() == False:
        display.fill(0)
        fbuf.fill(0)
        fbuf.text("Connecting...", 0, 0)
        display.blit(fbuf, 0, 0, 0)
        display.show()
        sleep(1)

    # Print the IP address of the Pico
    display.fill(0)
    fbuf.fill(0)
    fbuf.text("Connected.", 0, 0)
    fbuf.text("Pico IP: ", 0, 20)
    fbuf.text(str(wlan.ifconfig()[0]), 0, 40)
    display.blit(fbuf, 0, 0, 0)
    display.show()

# Main program
connect_wlan()
