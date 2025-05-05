# The idea of the code:

# The user can set three things using the OLED display and button:
# 1. Set soil moisture level - tell the program what's the desired level.
# 2. Set watering threshold - if the moisture is below the threshold, the pump starts (automatically).
# - The moisture is measured as 2 mins average.
# - If you set the threshold to "auto", the program automatically calculates 90 % of the desired level to be the threshold
# 3. Set pump run time - how long the pump should run once its started.
# - If you set it to "auto", the program first sets it to 1.0 s. Then after every time the pump has run, 
#   it measures if there's too much or too little moisture (compared to the desired level) after running the pump. Then it automatically increases
#  the pump running time (1.0 -> 1.1 s) or decreases it (1.0 -> 0.9 s).
# 4. Start/stop the pump - you can manually start the pump whenever you want. Hold the button down for a few seconds to do it.
#  The pump will run as long as you have set the running time, and then automatically turn off (the text "pump on" will change to "pump off")

# Push the button once to change the option. Hold it down for three seconds to change the values.

# If you don't change any options it will use default values. Default and min and max values are set in array "options"

# The welcome screen shows a little animation and soil moisture and 2 mins average moisture.
# The moisture values should be between 0...100.
# When you run the program it will take 2 minutes before it shows the average moisture.


from machine import Pin, I2C, ADC, PWM
from ssd1306 import SSD1306_I2C
from umqtt.simple import MQTTClient
import ssl
import time
import network
import ujson
import framebuf

# WIFI CREDENTIALS
SSID = "YOUR WIFI NAME"
PASSWORD = "YOUR WIFI PASSWORD"

# INIT CONSTANTS
WIDTH = 128
HEIGHT = 64
T_LENGTH = 5

# INIT COMPONENTS
i2c = I2C(0,scl=Pin(17),sda=Pin(16),freq=200000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
fbuf = framebuf.FrameBuffer(bytearray(WIDTH * HEIGHT * 1), WIDTH, HEIGHT, framebuf.MONO_VLSB)
soil_sensor = ADC(Pin(28))
button = Pin(15, Pin.IN, Pin.PULL_UP)
ain1_pin = Pin(8, Pin.OUT)  # Example: GPIO 8
ain2_pin = Pin(9, Pin.OUT)  # Example: GPIO 9
pwm_a_pin = PWM(Pin(10))    # Example: GPIO 10 (PWM capable)
stby_pin = Pin(7, Pin.OUT)  # Example: GPIO 7

# Set PWM frequency
pwm_a_pin.freq(1000)  # 1kHz PWM frequency

# Azure IoT Hub Configuration
MQTT_HOSTNAME = "broker.emqx.io"
MQTT_TOPIC_SOIL = f"womm/soil_moisture"
MQTT_TOPIC_PUMP = f"womm/pump_operation"


class Option:
    def __init__(self, optionName, optionValue, currentOption, underAdjusting, lastAdjusted, firstLine, secondLine, use_autoMode, enable_autoMode, on_text, off_text, min_value, max_value, threshold):
        self.optionName = optionName
        self.optionValue = optionValue
        self.currentOption = currentOption
        self.underAdjusting = underAdjusting
        self.lastAdjusted = lastAdjusted
        self.firstLine = firstLine
        self.secondLine = secondLine
        self.use_autoMode = use_autoMode
        self.enable_autoMode = enable_autoMode
        self.on_text = on_text
        self.off_text = off_text
        self.min_value = min_value
        self.max_value = max_value
        self.threshold = threshold
        
options = [ Option("MoistureLevel", # the name of the option
                   80, # the value (DEFAULT VALUE)
                   False, # is this the current option
                   False, # is the user adjusting this option now
                   0, # time the option was last adjusted
                   "Set soil", # the first line of the oled screen text
                   "moisture", # the second line of the oled screen text
                   False, # if the auto mode is on or off
                   False, # if the auto mode can be used
                   "", # the on text for the pump on/off option
                   "", # the off text for the pump on/off option
                   1, # min value
                   100, # max value
                   1), # threshold when changing the value
            Option("Threshold",
                   50,
                   False,
                   False,
                   0,
                   "Set watering",
                   "threshold",
                   False,
                   True,
                   "",
                   "",
                   0,
                   99,
                   1),
            Option("PumpRunTime",
                   0.5,
                   False,
                   False,
                   0,
                   "Set pump run",
                   "time",
                   False,
                   True,
                   "",
                   "",
                   0.0,
                   6.0,
                   0.1),
            Option("PumpControl",
                   0,
                   False,
                   False,
                   0,
                   "Start/stop pump",
                   "",
                   False,
                   False,
                   "Pump on",
                   "Pump off",
                   0,
                   0,
                   0) ]


# Function to draw the welcome screen
def draw_welcome_screen(fbuf, welcome_screen_time_state, soil_moisture, soil_moisture_2min_avg):
    
    # time state, the text, x, y
    welcome_screen_1_texts = [[0, "Smart", 0, 0], [1, "Plant", 0, 15], [2, "Watering", 0, 30], [3, "System", 0, 45]]
    welcome_screen_2_texts = [[10, "Soil moist:", 0, 15], [10, str(round(soil_moisture)), 100, 15], [11, "Avg 2 min:", 0, 30], [11, str(round(soil_moisture_2min_avg)), 100, 30]]

    pl_x = 100
    pl_y = 0
    welcome_screen_1_plant_lines = [[pl_x-8, pl_y+40, pl_x+19, pl_y+40, 1], [pl_x-8, pl_y+45, pl_x+19, pl_y+45, 1], [pl_x-8, pl_y+40, pl_x-8, pl_y+45, 1], [pl_x+19, pl_y+40, pl_x+19, pl_y+45, 1], [pl_x-5, pl_y+45, pl_x-3, pl_y+62, 1], [pl_x+16, pl_y+45, pl_x+13, pl_y+62, 1], [pl_x-3, pl_y+62, pl_x+13, pl_y+62, 1], [pl_x+6, pl_y+15, pl_x+6, pl_y+40, 1], [pl_x-8, pl_y+25, pl_x+6, pl_y+30, 1], [pl_x+19, pl_y+25, pl_x+6, pl_y+30, 1], [pl_x+6, pl_y+3, pl_x+1, pl_y+10, 1], [pl_x+1, pl_y+10, pl_x+1, pl_y+16, 1], [pl_x+1, pl_y+16, pl_x+6, pl_y+23, 1], [pl_x+6, pl_y+3, pl_x+11, pl_y+10, 1], [pl_x+11, pl_y+10, pl_x+11, pl_y+16, 1], [pl_x+11, pl_y+16, pl_x+6, pl_y+23, 1], [pl_x-16, pl_y+21, pl_x-10, pl_y+19, 1], [pl_x-10, pl_y+19, pl_x-5, pl_y+21, 1], [pl_x-5, pl_y+21, pl_x, pl_y+27, 1], [pl_x-16, pl_y+21, pl_x-13, pl_y+26, 1], [pl_x-13, pl_y+26, pl_x-7, pl_y+29, 1], [pl_x-7, pl_y+29, pl_x, pl_y+27, 1], [pl_x+26, pl_y+21, pl_x+20, pl_y+21, 1], [pl_x+20, pl_y+21, pl_x+16, pl_y+23, 1], [pl_x+16, pl_y+23, pl_x+10, pl_y+27, 1], [pl_x+10, pl_y+27, pl_x+19, pl_y+29, 1], [pl_x+19, pl_y+29, pl_x+24, pl_y+26, 1], [pl_x+24, pl_y+26, pl_x+26, pl_y+21, 1]]
    # x1, y1, x2, y2, color. First flowerpot, then upper leave, then left leave, then right leave

    welcome_screen_1_flowerpot_filling_lines = [[2, pl_x-3, 61, pl_x+13, 61, 1], [2, pl_x-3, 60, pl_x+13, 60, 1], [2, pl_x-3, 59, pl_x+13, 59, 1], [3, pl_x-3, 58, pl_x+13, 58, 1], [3, pl_x-3, 57, pl_x+13, 57, 1], [3, pl_x-3, 56, pl_x+13, 56, 1], [4, pl_x-3, 55, pl_x+13, 55, 1], [4, pl_x-3, 54, pl_x+13, 54, 1], [4, pl_x-3, 53, pl_x+15, 53, 1], [5, pl_x-3, 52, pl_x+15, 52, 1], [5, pl_x-3, 51, pl_x+15, 51, 1], [5, pl_x-3, 50, pl_x+15, 50, 1], [6, pl_x-4, 49, pl_x+15, 49, 1], [6, pl_x-4, 48, pl_x+15, 48, 1], [6, pl_x-4, 47, pl_x+15, 47, 1]]
    # welcome_screen_time_state, x1, y1, x2, y2, color.

    if welcome_screen_time_state < 10: # screen number 1
        for i in welcome_screen_1_texts:
            if welcome_screen_time_state >= i[0]:
                fbuf.text(i[1], i[2], i[3]) # draw texts
        for i in welcome_screen_1_plant_lines:
            if welcome_screen_time_state >= 0:
                fbuf.line(i[0], i[1], i[2], i[3], i[4]) # draw plant lines
        for i in welcome_screen_1_flowerpot_filling_lines:
            if welcome_screen_time_state >= i[0]:
                fbuf.line(i[1], i[2], i[3], i[4], i[5]) # draw flowerpot filling lines
    elif welcome_screen_time_state >= 10: # screen number 2
        for i in welcome_screen_2_texts:
            if welcome_screen_time_state >= i[0]:
                fbuf.text(i[1], i[2], i[3]) # draw texts

    return fbuf


# Function to find out if the user is adjusting some option value now
def adjusting_value(options):
    for i in options:
        if i.underAdjusting:
            return True
    return False

# Function to get option index by name
def get_option(options, OptionName):
    for i in options:
        if i.optionName == OptionName:
            return options.index(i)
    return false

# Function to disable options during welcome screen
def disable_options(options):
    for i in options:
        i.currentOption = False
    return options

# Function to set an option (by index) o be the current option
def switch_on_option(options, new_option_index):
    for i in options:
        i.currentOption = False
    if new_option_index < len(options):
        options[new_option_index].currentOption = True
    else:
        options[0].currentOption = True
    return options
     
# Function to return the index of the current option
def current_option(options):
    for i in options:
        if i.currentOption:
            return options.index(i)
    return -1

# Function to get the last time some option was adjusted
def get_last_time_option_was_adjusted(options):
    a = 0
    for i in options:
        if i.lastAdjusted > a:
            a = i.lastAdjusted
    return a

# Function to change variable values using OLED display and button
def set_options(fbuf, options, button_current_state, button_down_counter, button_previous_state, welcome_screen, welcome_screen_opened_time, welcome_screen_time_counter, pump_is_on, pump_off_time, pump_on_again_time, stop_flashing):
    # if the button is pressed or released or you're adjusting an option value
    if button_current_state != button_previous_state or adjusting_value(options):

        
        # hide the welcome screen (if opened) and start a counter to next welcome screen (5 seconds)
        welcome_screen = False
        welcome_screen_opened_time = 0
        welcome_screen_time_counter = time.ticks_ms() + 5000
        
        button_previous_state = button_current_state
        
        # if the button is down, wait three seconds before you can start adjusting an option value
        if button_current_state == 0 and not adjusting_value(options):
            button_down_counter = time.ticks_ms() + 3000
            
        # if the button is released and you're not adjusting any option, select next option
        if button_current_state == 1 and not adjusting_value(options):
            
            button_down_counter = 0 # if you've been holding the button down, you have to start again if you're going to adjust a value
            
            # select next option
            # if its more than 1 second since the last time an option value was changed
            # (1 second is to prevent that you won't select next option by accident)
            if time.ticks_ms() > (get_last_time_option_was_adjusted(options) + 1000):
                if current_option(options) >= len(options):
                    options = switch_on_option(options, 0)
                else:
                    options = switch_on_option(options, current_option(options) + 1)

        # if some option is selected, draw it on the oled
        if current_option(options) != -1:
            fbuf.fill(0)
            fbuf.text(options[current_option(options)].firstLine, 0, 8) # write the first text line
            fbuf.text(options[current_option(options)].secondLine, 0, 20) # write the second text line
            
            # if there's an auto mode, write "auto" on the oled
            if (options[current_option(options)].enable_autoMode and options[current_option(options)].optionValue == 0) or options[current_option(options)].use_autoMode:
                fbuf.text("Auto", 80, 40)
                options[current_option(options)].use_autoMode = True
            else:
                options[current_option(options)].use_autoMode = False
                
            # with the pump on/off option, write either "pump on" or "pump off"
            if options[current_option(options)].optionName == "PumpControl":
                if options[current_option(options)].optionValue == 1:
                    fbuf.text(options[current_option(options)].on_text, 50, 40) # on text
                else:
                    fbuf.text(options[current_option(options)].off_text, 50, 40) # off text
            # else: write option value on oled (if not auto or on/off)
            elif not options[current_option(options)].use_autoMode:
                fbuf.text(str(round(options[current_option(options)].optionValue, 1)), 80, 40)
                
            # drawing the option screen to oled display
            draw_on_oled(fbuf, stop_flashing)
            
            if options[current_option(options)].use_autoMode and adjusting_value(options):
               pass # if you're going to set the option to "auto", it's good to have a little break so it's easier to set it there 
        

    # if the button has been pressed three seconds and the button is down now, start changing the option value
    if time.ticks_ms() > button_down_counter and button_down_counter != 0 and button_current_state == 0 and not welcome_screen:
        options[current_option(options)].underAdjusting = True
        welcome_screen_time_counter = 0 # disable welcome screen counter
        if options[current_option(options)].optionName != "PumpControl":
            if options[current_option(options)].use_autoMode:
                options[current_option(options)].optionValue = 0
                options[current_option(options)].use_autoMode = False
            options[current_option(options)].optionValue += options[current_option(options)].threshold # increase option value, except not with the pump on/off option
            options[current_option(options)].lastAdjusted = time.ticks_ms()
            if options[current_option(options)].optionValue > options[current_option(options)].max_value: # if the option value is now > max, set it to min
                options[current_option(options)].optionValue = options[current_option(options)].min_value
            if options[current_option(options)].optionValue == 0 and options[current_option(options)].optionName == "PumpRunTime":
                options[current_option(options)].use_autoMode = True
                options[get_option(options, "PumpRunTime")].optionValue = 1.0
                button_down_counter = time.ticks_ms() + 1000
            elif options[current_option(options)].optionValue == 0 and options[current_option(options)].optionName == "Threshold":
                options[current_option(options)].use_autoMode = True
                button_down_counter = time.ticks_ms() + 1000
        time.sleep(0.1)

    # if you're adjusting the "pump on" option value, turn the pump on
    if adjusting_value(options) and options[current_option(options)].optionName == "PumpControl":
        if pump_off_time == 0 and ((time.ticks_ms() > pump_on_again_time) or ((time.ticks_ms() + 7000) < (pump_on_again_time - 3000))):
            options[current_option(options)].optionValue = 1
            start_pump("(MANUALLY)")
            pump_off_time = time.ticks_ms() + options[get_option(options, "PumpRunTime")].optionValue * 1000
            pump_is_on = True
            pump_on_again_time = pump_off_time + 10000

    # stop adjusting the option value if the button is up
    if adjusting_value(options) and button_current_state == 1:
        options[current_option(options)].underAdjusting = False
        button_down_counter = time.ticks_ms() + 3000
        welcome_screen_time_counter = time.ticks_ms() + 5000
        
        # you have to check that the watering threshold isn't higher than the moisture level you want to have
        # otherwise your plant will never get water
        if options[get_option(options, "Threshold")].optionValue > options[get_option(options, "MoistureLevel")].optionValue:
            options[get_option(options, "Threshold")].optionValue = options[get_option(options, "MoistureLevel")].optionValue - 1
    
    # auto adjust the threshold if in auto mode: 90 % of the desired moisture value
    if options[get_option(options, "Threshold")].use_autoMode:
        options[get_option(options, "Threshold")].optionValue = int(options[get_option(options, "MoistureLevel")].optionValue * 0.9)

    # check if it's time to show the welcome screen
    if time.ticks_ms() > welcome_screen_time_counter and welcome_screen_time_counter != 0:
        welcome_screen = True

    # check if the pump is off and the "pump off" text has to be written on OLED display
    if pump_off_time == 0 and current_option(options) != -1 and options[current_option(options)].optionName == "PumpControl" and not welcome_screen:
        fbuf.fill(0)
        fbuf.text(str(options[current_option(options)].firstLine), 0, 8) # write the first line of the option text
        fbuf.text(str(options[current_option(options)].secondLine), 0, 20) # write the second line of the option text
        fbuf.text(options[current_option(options)].off_text, 50, 40) # write the "pump off" text
        # automatically drawing the "pump off" text to oled display
        draw_on_oled(fbuf, stop_flashing)
    
    return [fbuf, options, button_down_counter, button_previous_state, welcome_screen, welcome_screen_opened_time, welcome_screen_time_counter, pump_is_on, pump_off_time, pump_on_again_time]


# Function to connect to WLAN
def connect_wlan():
    # Connecting to the group WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print(SSID)

    # Attempt to connect once per second
    while wlan.isconnected() == False:
        oled.fill(0)
        oled.text("Connecting...", 0, 0)
        oled.show()
        time.sleep(1)

    # Print the IP address of the Pico
    oled.fill(0)
    oled.text("Connected.", 0, 0)
    oled.text(wlan.ifconfig()[0], 0, 20)
    oled.show()

# Connect to MQTT broker
def connect_mqtt():
    try:
        client = MQTTClient("pico_client_" + str(time.ticks_ms()), MQTT_HOSTNAME, 1883)
        client.connect(clean_session=True)
        print(f"Connecting to {MQTT_HOSTNAME}")
        return client
    except Exception as e:
        print(f"Error connecting to MQTT: {e}")
    return 0

# Publish a Message
def publish_moisture(client, moisture):
    try:
        payload = ujson.dumps({"moisture": moisture, "timestamp": time.time()})
        client.publish(MQTT_TOPIC_SOIL, payload.encode('utf-8'))
        print(f"Published: {payload} to {MQTT_TOPIC_SOIL}")
    except Exception as e:
        print(f"Error publishing message: {e}")

# Publish a Message
def publish_pump(client, time_in_sec):
    try:
        payload = ujson.dumps({"running_time": time_in_sec, "timestamp": time.time()})
        client.publish(MQTT_TOPIC_PUMP, payload.encode('utf-8'))
        print(f"Published: {payload} to {MQTT_TOPIC_PUMP}")
    except Exception as e:
        print(f"Error publishing message: {e}")

# Function to read sensor data
def get_moisture():
    # value adc_air 50k = dry
    # value adc_water 25k = wet
    # moisture_percentage = ((adc_air - raw_value) / (adc_air - adc_water)) * 100
    adc_air = 52000
    adc_water = 24000
    raw_value = soil_sensor.read_u16()
    moisture_percent = ((adc_air - raw_value)/(adc_air - adc_water)) * 100
    # moisture_percent = (raw_value - adc_air) / (adc_water - adc_air) * 100
    # THESE VALUES SHOULD BE BETWEEN 0 AND 100!!!
    return round(moisture_percent, 2)

# Function to store 24 soil moisture values into an array (if measured every 5 seconds, 24 values = 2 minutes)
def add_moisture_to_array(soil_moisture_values, newest_value):
    soil_moisture_values.append(newest_value)
    if len(soil_moisture_values) > 24:
        soil_moisture_values.pop(0)
    return soil_moisture_values

# Function to calculate average of 24 soil moisture values
def get_moisture_2min_avg(soil_moisture_values):
    if len(soil_moisture_values) < 24: # if there is less measurements than 24, return zero
        return 0
    else:
        return sum(soil_moisture_values) / len(soil_moisture_values) # return average of 24 measurements

# Set up pump
def setup_pump():
    """
    Sets up the pin modes and initializes the motor driver.
    """
    pwm_a_pin.freq(1000)  # 1kHz PWM frequency
    ain1_pin.init(Pin.OUT)
    ain2_pin.init(Pin.OUT)
    # pwm_a_pin is already set as PWM in the global definition
    stby_pin.init(Pin.OUT)

    # Enable the motor driver (take it out of standby)
    stby_pin.value(1)  # Set STBY HIGH


# Function to start the pump
def start_pump(start_type): # start_type (string) = "(MANUALLY)" or "(AUTOMATICALLY)" (to write the text to the console)
    print("\n\n*************\n\nSTART THE PUMP " + str(time.time()) + "" + start_type)
    
    # WE NEED CODE HERE TO START THE PUMP!
    ain1_pin.value(1)
    ain2_pin.value(0)

    # Set a constant speed (e.g., 75%)
    pwm_a_pin.duty_u16(int(0.2 * 65535))  # 20% speed

# Function to stop the pump
def stop_pump():
    print("\nSTOP THE PUMP " + str(time.time()) + "\n\n*************\n\n")
    
    # CODE HERE TO STOP THE PUMP!
    ain1_pin.value(0)
    ain2_pin.value(0)
    pwm_a_pin.duty_u16(0)

# Drawing fbuf on OLED display
def draw_on_oled(fbuf, stop_flashing):
    if time.ticks_ms() > stop_flashing:
        try:
            oled.fill(0)
            oled.blit(fbuf, 0, 0, 0)
            oled.show()
        except Exception: # sometimes sending MQTT message at the same time seems to give an exception
            pass


# Main
if __name__ == "__main__":
    
    stop_flashing = 0 # this is to prevent OLED screen flashing
    
    fbuf.fill(0)
    draw_on_oled(fbuf, stop_flashing)
    
    stop_flashing = time.ticks_ms() + 1000
    wlan = connect_wlan()
    mqtt_client = connect_mqtt()
    setup_pump()
    
    time.sleep(1)
    
    if mqtt_client is 0:
        print("Unable to connect to MQTT")
        exit()


    # plant_1_moisture = options[get_option(options, "MoistureLevel")].optionValue
    # plant_1_threshold = options[get_option(options, "Threshold")].optionValue
    # pump_run_time = options[get_option(options, "PumpRunTime")].optionValue
    
    pump_is_on = False # is the pump on or off
    pump_is_published = False # has the pump on message been sent
    pump_off_time = 0 # timestamp when the pump will be turned of automatically
    pump_on_again_time = 0 # time when the pump can be run next time
    pump_delay = 60000 # wait 60 seconds after the pump has run before turning it again. This will make sure the pump won't run like in infinite loop
    pump_disabled_counter = 0 # this counts to three and if the soil is not getting moister when the pump is running, it will disable the pump
    
    soil_moisture = 0 # measured soil moisture
    soil_moisture_2min_avg = 0 # measured 2 min average soil moisture (average of 24 values)
    soil_moisture_values = [] # an array which contains soil moisture measurements (max. 24)
    soil_moisture_change_measuring_time = 0 # timestamp when it will measure the moisture again after running the pump
    soil_moisture_2min_avg_at_pump_on_moment = 0 # storing the 2 min avg moisture here when the pump is being turned on

    next_mqtt_message_time = time.ticks_ms() + 5000 # timestamp when the next Mqtt message should be sent
    
    welcome_screen = True # do we see welcome screen
    welcome_screen_opened_time = 0 # the time when the welcome screen is opened
    welcome_screen_time_state = 0 # counting from 0 to 19 to do animation
    welcome_screen_time_counter = 0 # timestamp when it will open the welcome screen

    button_down_counter = 0 # time to detect if the button is down 3s or more
    pump_on_again_time = 0 
    button_previous_state = 1 # the status of the button
    

    while True:
        
        # IF NEEDED, TURNING THE PUMP ON

        # if the plant needs to be watered - turn the pump on
        if not pump_is_on and soil_moisture_2min_avg < options[get_option(options, "Threshold")].optionValue and soil_moisture_2min_avg != 0 and time.ticks_ms() > pump_on_again_time and pump_disabled_counter < 3:
            start_pump("(AUTOMATICALLY)")
            pump_is_on = True
            pump_off_time = time.ticks_ms() + options[get_option(options, "PumpRunTime")].optionValue*1000 # time to switch off the pump
            pump_on_again_time = pump_off_time + pump_delay
            options[get_option(options, "PumpControl")].optionValue = 1
            
            # if there's 2 min moisture avg calculated and the pump is now put on, wait for two minutes and then measure 2 min avg moisture again
            if soil_moisture_2min_avg != 0 and soil_moisture_change_measuring_time == 0 and options[get_option(options, "PumpRunTime")].use_autoMode:
                soil_moisture_change_measuring_time = time.ticks_ms() + options[get_option(options, "PumpRunTime")].optionValue * 1000 + 120000
                print("\nStarted auto adjusting the pump running time - wait for 2 minutes")
                soil_moisture_2min_avg_at_pump_on_moment = soil_moisture_2min_avg
            elif soil_moisture_change_measuring_time == -1:
                soil_moisture_change_measuring_time = 0
                soil_moisture_2min_avg_at_pump_on_moment = 0
                # print("\n\nStopped auto adjusting the pump running time")
        elif pump_disabled_counter == 3: # if the system has been working badly three times
            print("\n\nXXXXXXXXXXXXX\n\nERROR: the system isn't working well, because despite pumping the water, the soil is not getting moist\n\nXXXXXXXXXXXXX\n\n")
            
            pump_disabled_counter = 0 # starting again, but if you really want to disable the pump, delete this line
            # use this to disable the pump:
            # pump_disabled_counter = 4 # adding one more to the value so it will show the message above only one time
                
        
        # AFTER THE PUMP HAS RUN, CHECKING IF THE PUMP RUN TIME VALUE HAS TO BE ADJUSTED
        
        # if the 2 min average moisture after pumping is more than the desired level, it will decrease the pump running time 0.1 s
        # and if the 2 min average moisture after pumping is less than the desired level, it will increase the pump running time 0.1 s
        if soil_moisture_change_measuring_time > 0 and time.ticks_ms() > soil_moisture_change_measuring_time:
            print("\n\nThe avg moisture after pumping was " +str(soil_moisture_2min_avg)+ " - before pumping it was: " + str(soil_moisture_2min_avg_at_pump_on_moment))
            if soil_moisture_2min_avg <= soil_moisture_2min_avg_at_pump_on_moment:
                pump_disabled_counter += 1 # in case the soil didn't get any moister, the counter disables the pump if the counter value reaches 3. Because something's wrong then
                print("\n\nSomething's wrong because the soil didn't get any more moist")
            else:
                pump_disabled_counter = 0 # in case the soil did get moister, everything is ok and we don't have to disable the pump
            if options[get_option(options, "PumpRunTime")].use_autoMode and soil_moisture_2min_avg > options[get_option(options, "MoistureLevel")].optionValue and options[get_option(options, "PumpRunTime")].optionValue > 0.1:
                options[get_option(options, "PumpRunTime")].optionValue -= 0.1 # auto adjust the pump running time
                print("\n\nThe avg moisture value now is higher than the desired level " + str(options[get_option(options, "MoistureLevel")].optionValue) + " so auto adjusting the pump running time to be 0.1 seconds shorter")
            elif options[get_option(options, "PumpRunTime")].use_autoMode and soil_moisture_2min_avg < options[get_option(options, "MoistureLevel")].optionValue:
                options[get_option(options, "PumpRunTime")].optionValue += 0.1 # auto adjust the pump running time
                print("\n\nThe avg moisture value now is lower than the desired level " + str(options[get_option(options, "MoistureLevel")].optionValue) + " so auto adjusting the pump running time to be 0.1 seconds longer")
            soil_moisture_change_measuring_time = -1


        # TURNING THE PUMP OFF
        
        # if the pump is on and there's some time defined when it should turn off
        if pump_is_on and pump_off_time != 0 and time.ticks_ms() > pump_off_time:
            stop_pump()
            pump_is_on = False
            pump_off_time = 0
            options[get_option(options, "PumpControl")].optionValue = 0
            
        
        # WELCOME SCREEN    

        # showing the picture of the plant or statistics
        if welcome_screen:
            if welcome_screen_opened_time == 0: # if the welcome screen is now opened
                welcome_screen_opened_time = time.ticks_ms() # take a timestamp
                
            # set a time counter that goes from 0 to 19 (for welcome screen animations)
            welcome_screen_time_state = round((time.ticks_ms() - welcome_screen_opened_time) / 1000) % 20
            # if welcome_screen_time_state is between 0-9: show screen number 1, between 10-19: show screen number 2
            options = disable_options(options) # disable setting any option during welcome screen
            
            # draw welcome screen on fbuf
            fbuf.fill(0)
            fbuf = draw_welcome_screen(fbuf, welcome_screen_time_state, soil_moisture, soil_moisture_2min_avg)
            draw_on_oled(fbuf, stop_flashing)
        
        
        # OPTIONS SCREEN
        
        # give all the option variables to function set_options()
        # it makes changes if needed and returns them back
        fbuf, options, button_down_counter, button_previous_state, welcome_screen, welcome_screen_opened_time, welcome_screen_time_counter, pump_is_on, pump_off_time, pump_on_again_time = set_options(fbuf, options, button.value(), button_down_counter, button_previous_state, welcome_screen, welcome_screen_opened_time, welcome_screen_time_counter, pump_is_on, pump_off_time, pump_on_again_time, stop_flashing)
        

        
        # MEASURING THE MOISTURE AND SENDING MQTT MESSAGES
        
        # measuring and publishing the moisture every 5 seconds
        if time.ticks_ms() > next_mqtt_message_time:
            soil_moisture = get_moisture()
            soil_moisture_values = add_moisture_to_array(soil_moisture_values, soil_moisture)
            soil_moisture_2min_avg = get_moisture_2min_avg(soil_moisture_values)
            print("Settings: Moisture level: " + str(options[get_option(options, "MoistureLevel")].optionValue)+ ", Threshold: " + str(options[get_option(options, "Threshold")].optionValue) + ", Pump run time: " + str(options[get_option(options, "PumpRunTime")].optionValue))
            
            next_mqtt_message_time += 5000 # timestamp when the next Mqtt message should be sent
            stop_flashing = time.ticks_ms() + 100
            publish_moisture(mqtt_client, soil_moisture)
            time.sleep(0.2)
        
        # if the pump is on, publishing a message
        if pump_is_on and not pump_is_published:
            stop_flashing = time.ticks_ms() + 100
            publish_pump(mqtt_client, options[get_option(options, "PumpRunTime")].optionValue)
            pump_is_published = True
        elif not pump_is_on:
            pump_is_published = False


        
        # always sleeping 0.05 s
        time.sleep(0.05)
