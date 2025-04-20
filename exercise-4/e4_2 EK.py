from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf
import dht
import time
import network
from umqtt.simple import MQTTClient


# Replace these values with your own
SSID = "SmartIoTMQTT"
PASSWORD = "SmartIot"
# BROKER_IP = "192.168.1.254"
BROKER_IP = "broker.emqx.io"

# Function to connect to WLAN
def connect_wlan():
    # Connecting to the group WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    # Attempt to connect once per second
    while wlan.isconnected() == False:
        print("Connecting... ")
        time.sleep(1)

    # Print the IP address of the Pico
    print("Connection successful. Pico IP:", wlan.ifconfig()[0])
    
def send_mqtt(client, topic, message):
    client.publish(topic, message)
    print(f"Sending to MQTT: {topic} -> {message}")
    
def connect_mqtt():
    mqtt_client=MQTTClient("pico_test", BROKER_IP)
    mqtt_client.connect(clean_session=True)
    return mqtt_client



# Humidity and temperature sensor
data_pin = Pin(13, Pin.IN, Pin.PULL_UP)
sensor = dht.DHT22(data_pin)

class Sensor_data:
    def __init__(self, temperature, humidity):
        self.temperature = temperature
        self.humidity = humidity

def read_sensor():
    try:
        sensor.measure()
        return Sensor_data(sensor.temperature(), sensor.humidity())
    except OSError as e:
        print("Error reading data from the sensor")
        return Sensor_data(0, 0)

        


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
            measurement = read_sensor()
            send_mqtt(mqtt_client, "eelis/temperature", str(measurement.temperature))
            send_mqtt(mqtt_client, "eelis/humidity", str(measurement.humidity))
            time.sleep(5)
            
    except Exception as e:
        print(f"Failed to send MQTT message: {e}")

