import machine
import time

ad_pin = machine.ADC(4)

def calculate_voltage(ad):
    return (ad / (65536 - 1) * 3.3)

def calculate_temperature(voltage):
    return (27 - (voltage - 0.706) / (1.721/1000) )

while True:
    print(calculate_temperature(calculate_voltage(ad_pin.read_u16())))
    time.sleep(2)



"""
    print(calculate_temperature(calculate_voltage(14000)))
        prints 27.60031
    print(calculate_temperature(calculate_voltage(14001)))
        prints 27.57108
    so the smallest detectable change in temperature is about 0.03 Celsius

"""