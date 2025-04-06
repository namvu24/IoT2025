from machine import ADC, Pin, I2C
import time
import ssd1306

# Set up I2C for OLED
i2c = I2C(0, scl=Pin(17), sda=Pin(16))  # Adjust pins for I2C as needed
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Set up DHT22 sensor on GPIO15
temp_sensor = ADC(4)  # Internal temperature sensor (GPIO26)
# Array to store the last 5 temperature readings
temp_readings = []

# Function to calculate the temperature
def get_temperature(ad_value):
    # Convert AD value to voltage
    voltage = (ad_value / 65535) * 3.3
    # Apply the temperature transfer function
    temperature = 27 - ((voltage - 0.706) / 1.721)
    return temperature

# Function to calculate the average of the last 5 temperatures
def calculate_average(temperatures):
    return sum(temperatures) / len(temperatures)

while True:
    # Read the analog value from the temperature sensor
    ad_value = temp_sensor.read_u16()
    
    # Calculate the temperature from the AD value
    temperature = get_temperature(ad_value)
    
    # Add the new temperature reading to the list
    temp_readings.append(temperature)
    
    # If the list exceeds 5 elements, remove the oldest reading
    if len(temp_readings) > 5:
        temp_readings.pop(0)
    
    # Calculate the floating average of the last 5 temperatures
    avg_temperature = calculate_average(temp_readings)
    
    # Print the average temperature to the OLED display
    oled.fill(0)  # Clear the display
    oled.text("Avg Temperature", 0, 0)
    oled.text(f'{avg_temperature:.2f} C', 0, 16)
    oled.show()
    
    # Wait for 1 second before the next reading
    time.sleep(1)
