import machine
import time
analog_value = machine.ADC(28)

def calculate_temperature(voltage):
    return (27 - (voltage-0.706)/1.721)

def calculate_voltage(ad):
    return (ad * 3.3/65535)
 
while True:
    ad = analog_value.read_u16()
    temperature = calculate_temperature(calculate_voltage(ad))
    print("Temperature: ", temperature)
    time.sleep(2)