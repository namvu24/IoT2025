from machine import Pin
from time import sleep


led = Pin("LED", Pin.OUT)  

# Timings in seconds
DIT = 0.5
DAH = 1.5
CHAR_GAP = 0.5
LETTER_GAP = 1.5
MESSAGE_GAP = 3.5

def blink(duration, symbol):
    print(f"Blinking {symbol} for {duration} seconds")
    led.on()
    sleep(duration)
    led.off()
    sleep(CHAR_GAP)

def morse_s():
    print("Sending: S")
    for _ in range(3):
        blink(DIT, ".")
    sleep(LETTER_GAP - CHAR_GAP)

def morse_o():
    print("Sending: O")
    for _ in range(3):
        blink(DAH, "-")
    sleep(LETTER_GAP - CHAR_GAP)

# Loop forever
while True:
    print("\n--- SOS Sequence Start ---")
    morse_s()
    morse_o()
    morse_s()
    print("--- SOS Sequence End ---\n")
    sleep(MESSAGE_GAP)
