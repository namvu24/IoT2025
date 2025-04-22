from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
from umqtt.simple import MQTTClient
import ssl
import time
import network
import ujson
import config

CONNECT_WIFI = False

# Credentials from config.py
SSID = config.SSID
PASSWORD = config.PASSWORD
IOT_HUB_HOSTNAME = config.IOT_HUB_HOSTNAME
DEVICE_ID = config.DEVICE_ID
SAS_TOKEN = config.SAS_TOKEN

# INIT CONSTANTS
WIDTH = 128
HEIGHT = 64
T_LENGTH = 5

# INIT COMPONENTS
i2c = I2C(0,scl=Pin(17),sda=Pin(16),freq=200000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
soil_sensor = ADC(Pin(28))

# Azure IoT Hub Configuration
MQTT_CLIENT_ID = DEVICE_ID
MQTT_USERNAME = f"{IOT_HUB_HOSTNAME}/{DEVICE_ID}/?api-version=2021-04-12"
MQTT_PASSWORD = SAS_TOKEN
MQTT_TOPIC = f"devices/{DEVICE_ID}/messages/events/"

# Function to connect to WLAN
def connect_wlan():
    # Connecting to the group WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print(SSID)

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

# Connect to Azure IoT Hub using MQTT
def connect_mqtt():
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.verify_mode = ssl.CERT_NONE
        client = MQTTClient(
            client_id=MQTT_CLIENT_ID,
            server=IOT_HUB_HOSTNAME,
            port=8883,
            user=MQTT_USERNAME,
            password=MQTT_PASSWORD,
            ssl=context
        )
        client.connect()
        print("Connected to Azure IoT Hub")
        return client
    except Exception as e:
        print(f"Error connecting to MQTT: {e}")
        return None

# Publish a Message
def publish_moisture(client, moisture):
    try:
        payload = ujson.dumps({"moisture": moisture, "timestamp": time.time()})
        if CONNECT_WIFI:
            client.publish(MQTT_TOPIC, payload.encode('utf-8'))
        print(f"Published: {payload} to {MQTT_TOPIC}")
    except Exception as e:
        print(f"Error publishing message: {e}")

# Function to read sensor data
def get_moisture():
    # value adc_air 50k = dry
    # value adc_water 25k = wet
    # moisture_percentage = ((adc_air - raw_value) / (adc_air - adc_water)) * 100
    adc_air = 52000
    adc_water = 24000
    raw_value = soil_sensor.read_u16()
    moisture_percent = ((adc_air - raw_value)/(adc_air - adc_water)) * 100
    return round(moisture_percent, 2)

# Main
if __name__ == "__main__":
    wlan = None
    mqtt_client = None
    
    if CONNECT_WIFI:
        wlan = connect_wlan()
        mqtt_client = connect_mqtt()
    else:
        print("OFFLINE MODE.")

    try:
        while True:
            soil_moisture = get_moisture()
            print(soil_moisture)
            oled.fill(0)
            oled.text(f"Moisture data", 0, 0)
            oled.text(f"{soil_moisture}", 0, 20)
            oled.show()
            publish_moisture(mqtt_client, soil_moisture)
            time.sleep(1)  # Send data every 5 seconds
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        mqtt_client.disconnect()
        wlan.disconnect()
