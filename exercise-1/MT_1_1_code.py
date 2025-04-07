from machine import Pin
import time

led = Pin("LED", Pin.OUT)

morse_code = {
    "S": "...",
    "O": "---"
}

def blink_morse_code(code):
    for symbol in code:
        if symbol == ".":
            led.on()  # Turn on LED for a short period (dit)
            time.sleep(0.5)  
            led.off()  # Turn off LED
            time.sleep(0.5)  
        elif symbol == "-":
            led.on()  # Turn on LED for a long period (dah)
            time.sleep(1.5)  
            led.off()  # Turn off LED
            time.sleep(0.5)  
    
def blink_sos():
    while True:
        # Blink 'S' (3 dots), then 'O' (3 dashes), then 'S' again
        blink_morse_code(morse_code["S"])
        time.sleep(1.5)  
        blink_morse_code(morse_code["O"])
        time.sleep(1.5)  
        blink_morse_code(morse_code["S"])
        time.sleep(3.5) 


blink_sos()
