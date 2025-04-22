from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
from umqtt.simple import MQTTClient
import ssl
import time
import network
import ujson

# WIFI CREDENTIALS
SSID = "WIFI_SSID"
PASSWORD = "WIFI_PWD"

# INIT CONSTANTS
WIDTH = 128
HEIGHT = 64
T_LENGTH = 5

# INIT COMPONENTS
i2c = I2C(0,scl=Pin(17),sda=Pin(16),freq=200000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
soil_sensor = ADC(Pin(28))

# Azure IoT Hub Configuration
MQTT_HOSTNAME = "broker.emqx.io"
MQTT_TOPIC_SOIL = f"womm/soil_moisture"
MQTT_TOPIC_PUMP = f"womm/pump_operation"

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

# Connect to MQTT broker
def connect_mqtt():
    try:
        client = MQTTClient("pico_client_" + str(time.ticks_ms()), MQTT_HOSTNAME, 1883)
        client.connect(clean_session=True)
        print(f"Connecting to {MQTT_HOSTNAME}")
        return client
    except Exception as e:
        print(f"Error connecting to MQTT: {e}")
        return None

# Publish a Message
def publish_moisture(client, moisture):
    try:
        payload = ujson.dumps({"moisture": moisture, "timestamp": time.time()})
        client.publish(MQTT_TOPIC_SOIL, payload.encode('utf-8'))
        print(f"Published: {payload} to {MQTT_TOPIC_SOIL}")
    except Exception as e:
        print(f"Error publishing message: {e}")

# Publish a Message
def publish_pump(client, time_in_sec):
    try:
        payload = ujson.dumps({"running_time": time_in_sec, "timestamp": time.time()})
        client.publish(MQTT_TOPIC_PUMP, payload.encode('utf-8'))
        print(f"Published: {payload} to {MQTT_TOPIC_PUMP}")
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
    wlan = connect_wlan()
    mqtt_client = connect_mqtt()
    
    if mqtt_client is None:
        print("Unable to connect to MQTT")
        exit()

    plant_1_threshold = input("plant 1 moisture: ")
    pump_run_time = input("pump run time: ")

    while True:
        soil_moisture = get_moisture()
        print(soil_moisture)
        oled.fill(0)
        oled.text(f"Moisture data", 0, 0)
        oled.text(f"{soil_moisture}", 0, 20)
        oled.show()
        publish_moisture(mqtt_client, soil_moisture)
        if soil_moisture <= float(plant_1_threshold):
            #start_pump(time=pump_run_time)
            publish_pump(mqtt_client, pump_run_time)
        time.sleep(5)  # Send data every 5 seconds
