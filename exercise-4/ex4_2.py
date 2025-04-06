import network
import time
import dht
from umqtt.simple import MQTTClient
from machine import Pin, I2C
import ssd1306

# Wi-Fi credentials
SSID = "SSID"
PASSWORD = "WIFI_PASS"
BROKER_IP = "34.243.217.54"

# Set up I2C for OLED display (optional, for monitoring)
i2c = I2C(0, scl=Pin(17), sda=Pin(16))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Set up DHT22 sensor on GPIO15
sensor = dht.DHT22(Pin(15))

# MQTT setup
CLIENT_ID = "mqttx_f5664edc"
TOPIC_BASE = "emmanuel"

# Function to connect to Wi-Fi
def connect_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        time.sleep(1)

    print("Wi-Fi connected, IP:", wlan.ifconfig()[0])

# Function to publish messages to MQTT
def publish_message(client, topic, message):
    client.connect()
    client.publish(topic, message)
    print(f"Message sent to {topic}: {message}")
    client.disconnect()

# Function to read temperature and humidity and publish them
def read_and_publish(client):
    # Read temperature and humidity from DHT22
    try:
        sensor.measure()
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        
        # Print on OLED (optional)
        oled.fill(0)
        oled.text(f"Temp: {temperature}C", 0, 0)
        oled.text(f"Humidity: {humidity}%", 0, 16)
        oled.show()
        
        # Publish the temperature and humidity to separate topics
        publish_message(client, f"{TOPIC_BASE}/temperature", str(temperature))
        publish_message(client, f"{TOPIC_BASE}/humidity", str(humidity))
    except OSError as e:
        print("Failed to read sensor data:", e)

# Main program
def main():
    connect_wlan()

    # Create an MQTT client instance
    client = MQTTClient(CLIENT_ID, BROKER_IP)

    # Loop to read and publish data every 5 seconds
    while True:
        read_and_publish(client)
        time.sleep(5)

if __name__ == "__main__":
    main()
