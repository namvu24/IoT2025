from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time
import network

# INIT CONSTANTS
WIDTH = 128
HEIGHT = 64
T_LENGTH = 5

# NETWORK CONSTANTS
SSID = "SmartIoTMQTT"
PASSWORD = "SmartIot"
BROKER_IP = "192.168.1.254"


# INIT COMPONENTS
i2c = I2C(0,scl=Pin(17),sda=Pin(16),freq=200000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Function to connect to WLAN
def connect_wlan():
    # Connecting to the group WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    # Attempt to connect once per second
    while wlan.isconnected() == False:
        oled.fill(0)
        oled.text("Connecting...", 0, 0)
        oled.show()
        time.sleep(1)

    # Print the IP address of the Pico
    oled.fill(0)
    oled.text("Connected.", 0, 0)
    oled.text(wlan.ifconfig()[0], 0, 20)
    oled.show()

connect_wlan()