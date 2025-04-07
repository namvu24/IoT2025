from machine import ADC
import time

# Constants
ADC_RESOLUTION = 65535 
VREF = 3.3  
TEMP_SENSOR_ADC = 4  

def read_temperature():
    adc = ADC(TEMP_SENSOR_ADC)
    adc_value = adc.read_u16()  
    voltage = (adc_value / ADC_RESOLUTION) * VREF
    temperature = 27 - ((voltage - 0.706) / 0.001721)

    return adc_value, voltage, temperature

while True:
    adc_value, voltage, temperature = read_temperature()
    print(f"ADC Value: {adc_value}, Voltage: {voltage:.3f} V, Temperature: {temperature:.2f} °C")
    time.sleep(2)
