import network
from time import sleep
import ssd1306
from machine import Pin, I2C

# Replace these values with your own
SSID = "Koti_648A"
PASSWORD = "WIFI_PASS"
BROKER_IP = "34.243.217.54"

i2c = I2C(0, scl=Pin(17), sda=Pin(16))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Function to connect to WLAN
def connect_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    oled.fill(0)  # Clear the display
    oled.text("Connecting...", 0, 0)
    oled.show()
    
    
    while not wlan.isconnected():
        sleep(1)

    # Once connected, show "Connected" and the IP address on OLED
    oled.fill(0)  # Clear the display
    oled.text("Connected", 0, 0)
    oled.text("IP: " + wlan.ifconfig()[0], 0, 16)  # Display IP address
    oled.show()

# Main program
connect_wlan()

