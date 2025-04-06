from machine import ADC, Pin
import time

# Define the internal temperature sensor (on the ADC channel 4)
temp_sensor = ADC(4)  # Pin 26 for the internal temperature sensor

# Function to calculate the temperature
def get_temperature(ad_value):
    # Convert AD value to voltage
    voltage = (ad_value / 65535) * 3.3
    # Apply the temperature transfer function
    temperature = 27 - ((voltage - 0.706) / 1.721)
    return temperature, voltage

while True:
    # Read the analog value from the temperature sensor
    ad_value = temp_sensor.read_u16()
    
    # Calculate the temperature and voltage
    temperature, voltage = get_temperature(ad_value)
    
    # Print the AD value and the calculated temperature
    print(f"AD Value: {ad_value}, Voltage: {voltage:.4f}V, Temperature: {temperature:.2f}°C")
    
    # Wait for 2 seconds before the next reading
    time.sleep(2)
