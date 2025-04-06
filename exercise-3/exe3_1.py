from machine import Pin, I2C
import time
import ssd1306
import dht

# Set up I2C and OLED
i2c = I2C(0, scl=Pin(17), sda=Pin(16))  
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Set up DHT22 sensor on GPIO15
dht22 = dht.DHT22(Pin(15))

# Function to display temperature and humidity
def display_data(temperature, humidity):
    oled.fill(0) 
    oled.text('Temperature:', 0, 0)
    oled.text(f'{temperature}C', 0, 16)  
    oled.text('Humidity:', 0, 32)
    oled.text(f'{humidity}%', 0, 48)  
    oled.show()

while True:
    try:
        dht22.measure()  
        temperature = dht22.temperature()  
        humidity = dht22.humidity()  
        
        display_data(temperature, humidity)  

    except OSError as e:
        print('Failed to read sensor data')

    time.sleep(1)  
