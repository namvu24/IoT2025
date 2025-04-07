from machine import Pin
import time

# DEFINE COMPONENTS
led = Pin("LED", Pin.OUT)

# DEFINE CONTSTANTS
DASH_WAIT = 1500
DOT_WAIT = 500
LETTER_WAIT = 1500
CHAR_WAIT = 500
MESSAGE_WAIT = 3500

# DEFINE FUNCTIONS
def display_char(wait_time):
    led.on()
    time.sleep_ms(wait_time)
    led.off()
    
def display_letter(letter):
    print(letter)
    if letter == 'S':
        display_char(DOT_WAIT)
        time.sleep_ms(CHAR_WAIT)
        display_char(DOT_WAIT)
        time.sleep_ms(CHAR_WAIT)
        display_char(DOT_WAIT)
        time.sleep_ms(CHAR_WAIT)
    elif letter == 'O':
        display_char(DASH_WAIT)
        time.sleep_ms(CHAR_WAIT)
        display_char(DASH_WAIT)
        time.sleep_ms(CHAR_WAIT)
        display_char(DASH_WAIT)
        time.sleep_ms(CHAR_WAIT)

def main():
    print('START')
    display_letter('S')
    time.sleep_ms(LETTER_WAIT)
    display_letter('O')
    time.sleep_ms(LETTER_WAIT)
    display_letter('S')
    time.sleep_ms(MESSAGE_WAIT)
    print('STOP')

# START MAIN
while True:
    main()



    
    