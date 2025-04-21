from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time
import network
from umqtt.simple import MQTTClient
import dht

# INIT CONSTANTS
WIDTH = 128
HEIGHT = 64
T_LENGTH = 5

# NETWORK CONSTANTS
SSID = "SmartIoTMQTT"
PASSWORD = "SmartIot"
BROKER_IP = "192.168.1.254"
MQTT_TOPIC_T = "/nam/temperature"
MQTT_TOPIC_H = "/nam/humidity"

# INIT COMPONENTS
i2c = I2C(0,scl=Pin(17),sda=Pin(16),freq=200000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
data_pin = Pin(13, Pin.IN, Pin.PULL_UP)
sensor = dht.DHT22(data_pin)

def read_sensor_temperature():
    try:
        sensor.measure()
        temperature = sensor.temperature()
        print(f"Temperature: {temperature}")
    except OSError as e:
        print("Error reading data from the sensor")
    return temperature
        
def read_sensor_humidity():
    try:
        sensor.measure()
        humidity = sensor.humidity()
        print(f"Humidity: {humidity}")
    except OSError as e:
        print("Error reading data from the sensor")
    return humidity

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

def connect_mqtt():
    mqtt_client=MQTTClient("", BROKER_IP)
    mqtt_client.connect(clean_session=True)
    return mqtt_client

# Main program
if __name__ == "__main__":
    #Connect to WLAN
    connect_wlan()
    
    # Connect to MQTT
    try:
        mqtt_client=connect_mqtt()
    except Exception as e:
        print(f"Failed to connect to MQTT: {e}")

    # Send MQTT message
    try:
        while True:
            # Sending a message every 5 seconds.
            read_sensor()
            
            # Temperature
            temperature = read_sensor_temperature()
            mqtt_client.publish(MQTT_TOPIC_T, temperature)
            print(f"Sending to MQTT: {MQTT_TOPIC_T} -> {temperature}")
            
            # Humidity
            humidity = read_sensor_humidity()
            mqtt_client.publish(MQTT_TOPIC_H, humidity)
            print(f"Sending to MQTT: {MQTT_TOPIC_H} -> {humidity}")
            
            time.sleep(5)
            
    except Exception as e:
        print(f"Failed to send MQTT message: {e}")


connect_wlan()