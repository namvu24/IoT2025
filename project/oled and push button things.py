# The idea of the code:

# The user can set three things using the OLED display and button:
# 1. Set soil moisture level - tell the program what's the desired level.
# 2. Set watering threshold - if the moisture is below the threshold, the pump starts.
# - The moisture is measured as 2 mins average.
# - If you set it to "auto", the program automatically calculates 90 % of the desired level
# 3. Set pump run time - how long the pump should run once its started.
# - If you set it to "auto", the program automatically increases or decreases the running time,
#   if it detects that there's too much or too little moisture after running the pump.
# 4. Start/stop the pump - you can manually start the pump whenever you want. Hold the button down for a few seconds to do it.

# Push button once to change the option and hold it down to change the values.

# The welcome screen shows a little animation and soil moisture and 2 mins average moisture.
# When you run the program it will take 2 minutes before it shows the average moisture.


from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
from umqtt.simple import MQTTClient
import ssl
import time
import network
import ujson
import framebuf

# WIFI CREDENTIALS
SSID = "Leppaniitty-langaton"
PASSWORD = "channel9001"

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

# Azure IoT Hub Configuration
MQTT_HOSTNAME = "broker.emqx.io"
MQTT_TOPIC_SOIL = f"womm/soil_moisture"
MQTT_TOPIC_PUMP = f"womm/pump_operation"


current_option = -1
welcome_screen = True
welcome_screen_opening_time = 0
sleep_order = 0
draw_on_oled = False

adjust_option = False
start_adjusting_value_counter = 0
just_stopped_adjusting = False
pump_turned_on = False
pump_on_again_counter = 0
welcome_screen_counter = 0
previous_button_state = 1 # the status of the button

class Option:
    def __init__(self, optionName, optionValue, firstLine, secondLine, autoMode, on_text, off_text, min_value, max_value, threshold):
        self.optionName = optionName
        self.optionValue = optionValue
        self.firstLine = firstLine
        self.secondLine = secondLine
        self.autoMode = autoMode
        self.on_text = on_text
        self.off_text = off_text
        self.min_value = min_value
        self.max_value = max_value
        self.threshold = threshold

options = [ Option("MoistureLevel", 10, "Set soil", "moisture", False, "", "", 1, 100, 1), Option("Threshold", 9, "Set watering", "threshold", True, "", "", 0, 100, 1), Option("PumpRunTime", 0.5, "Set pump run", "time", True, "", "", 0.0, 6, 0.1), Option("PumpControl", 0, "Start/stop pump", "", False, "Pump on", "Pump off", 0, 0, 0) ]


# Function to draw the welcome screen
def draw_welcome_screen(fbuf, time_state, soil_moisture, soil_moisture_2min_avg):
    
    # time state, the text, x, y
    welcome_screen_1_texts = [[0, "Smart", 0, 0], [1, "Plant", 0, 15], [2, "Watering", 0, 30], [3, "System", 0, 45]]
    welcome_screen_2_texts = [[10, "Soil moist:", 0, 15], [10, str(round(soil_moisture)), 100, 15], [11, "Avg 2 min:", 0, 30], [11, str(round(soil_moisture_2min_avg)), 100, 30]]

    pl_x = 100
    pl_y = 0
    welcome_screen_1_plant_lines = [[pl_x-8, pl_y+40, pl_x+19, pl_y+40, 1], [pl_x-8, pl_y+45, pl_x+19, pl_y+45, 1], [pl_x-8, pl_y+40, pl_x-8, pl_y+45, 1], [pl_x+19, pl_y+40, pl_x+19, pl_y+45, 1], [pl_x-5, pl_y+45, pl_x-3, pl_y+62, 1], [pl_x+16, pl_y+45, pl_x+13, pl_y+62, 1], [pl_x-3, pl_y+62, pl_x+13, pl_y+62, 1], [pl_x+6, pl_y+15, pl_x+6, pl_y+40, 1], [pl_x-8, pl_y+25, pl_x+6, pl_y+30, 1], [pl_x+19, pl_y+25, pl_x+6, pl_y+30, 1], [pl_x+6, pl_y+3, pl_x+1, pl_y+10, 1], [pl_x+1, pl_y+10, pl_x+1, pl_y+16, 1], [pl_x+1, pl_y+16, pl_x+6, pl_y+23, 1], [pl_x+6, pl_y+3, pl_x+11, pl_y+10, 1], [pl_x+11, pl_y+10, pl_x+11, pl_y+16, 1], [pl_x+11, pl_y+16, pl_x+6, pl_y+23, 1], [pl_x-16, pl_y+21, pl_x-10, pl_y+19, 1], [pl_x-10, pl_y+19, pl_x-5, pl_y+21, 1], [pl_x-5, pl_y+21, pl_x, pl_y+27, 1], [pl_x-16, pl_y+21, pl_x-13, pl_y+26, 1], [pl_x-13, pl_y+26, pl_x-7, pl_y+29, 1], [pl_x-7, pl_y+29, pl_x, pl_y+27, 1], [pl_x+26, pl_y+21, pl_x+20, pl_y+21, 1], [pl_x+20, pl_y+21, pl_x+16, pl_y+23, 1], [pl_x+16, pl_y+23, pl_x+10, pl_y+27, 1], [pl_x+10, pl_y+27, pl_x+19, pl_y+29, 1], [pl_x+19, pl_y+29, pl_x+24, pl_y+26, 1], [pl_x+24, pl_y+26, pl_x+26, pl_y+21, 1]]
    # x1, y1, x2, y2, color. First flowerpot, then upper leave, then left leave, then right leave

    welcome_screen_1_flowerpot_filling_lines = [[2, pl_x-3, 61, pl_x+13, 61, 1], [2, pl_x-3, 60, pl_x+13, 60, 1], [2, pl_x-3, 59, pl_x+13, 59, 1], [3, pl_x-3, 58, pl_x+13, 58, 1], [3, pl_x-3, 57, pl_x+13, 57, 1], [3, pl_x-3, 56, pl_x+13, 56, 1], [4, pl_x-3, 55, pl_x+13, 55, 1], [4, pl_x-3, 54, pl_x+13, 54, 1], [4, pl_x-3, 53, pl_x+15, 53, 1], [5, pl_x-3, 52, pl_x+15, 52, 1], [5, pl_x-3, 51, pl_x+15, 51, 1], [5, pl_x-3, 50, pl_x+15, 50, 1], [6, pl_x-4, 49, pl_x+15, 49, 1], [6, pl_x-4, 48, pl_x+15, 48, 1], [6, pl_x-4, 47, pl_x+15, 47, 1]]
    # time_state, x1, y1, x2, y2, color.

    if time_state < 10: # screen number 1
        for i in welcome_screen_1_texts:
            if time_state >= i[0]:
                fbuf.text(i[1], i[2], i[3]) # draw texts
        for i in welcome_screen_1_plant_lines:
            if time_state >= 0:
                fbuf.line(i[0], i[1], i[2], i[3], i[4]) # draw plant lines
        for i in welcome_screen_1_flowerpot_filling_lines:
            if time_state >= i[0]:
                fbuf.line(i[1], i[2], i[3], i[4], i[5]) # draw flowerpot filling lines
    elif time_state >= 10: # screen number 2
        for i in welcome_screen_2_texts:
            if time_state >= i[0]:
                fbuf.text(i[1], i[2], i[3]) # draw texts

    return fbuf


# Function to  change variable values using OLED display and button
def set_options(fbuf, options, current_button_state, current_option, welcome_screen, welcome_screen_opening_time, adjust_option, start_adjusting_value_counter, just_stopped_adjusting, pump_run_time, pump_on_again_counter, welcome_screen_counter, previous_button_state, sleep_order, draw_on_oled, pump_off_time, pump_turned_on, set_pump_run_time_to_1):
    # if the button is pressed or released or you're adjusting an option value
    if current_button_state != previous_button_state or adjust_option:
        previous_button_state = current_button_state
        
        # if the button is down, wait three seconds before you can start adjusting an option value
        if current_button_state == 0 and not adjust_option:
            start_adjusting_value_counter = time.ticks_ms() + 3000
            
        # if the button is released and you're not adjusting any option, select next option
        if current_button_state == 1 and not adjust_option and not just_stopped_adjusting:
            
            # hide the welcome screen (if opened) and start a counter to next welcome screen (5 seconds)
            welcome_screen = False
            welcome_screen_opening_time = 0
            welcome_screen_counter = time.ticks_ms() + 5000
            
            start_adjusting_value_counter = 0 # if you've been holding the button down, you have to start again if you're going to adjust a value
            
            current_option += 1 # select next option
            if current_option >= len(options):
                current_option = 0

        # if some option is selected, draw it on the oled
        if current_option != -1:
            fbuf.fill(0)
            fbuf.text(options[current_option].firstLine, 0, 8) # write the first text line
            fbuf.text(options[current_option].secondLine, 0, 20) # write the second text line
            
            # if there's an auto mode, write "auto" on the oled
            if options[current_option].autoMode and options[current_option].optionValue == 0:
                fbuf.text("Auto", 80, 40)
                
            # with the pump on/off option, write either "pump on" or "pump off"
            elif options[current_option].optionName == "PumpControl":
                if options[current_option].optionValue == 1:
                    fbuf.text(options[current_option].on_text, 50, 40) # on text
                else:
                    fbuf.text(options[current_option].off_text, 50, 40) # off text
            # else: write option value on oled (if not auto or on/off)
            else:
                fbuf.text(str(round(options[current_option].optionValue, 1)), 80, 40)
            draw_on_oled = True # tell the main function that something has to be drawn on the display now
            
            if options[current_option].autoMode and options[current_option].optionValue == 0 and adjust_option:
                sleep_order = 1 # if you're going to set the option to "auto", it's good to have a little break so it's easier to set it there 
        
        # after you have stopped adjusting, you have to check that the watering threshold isn't higher than the moisture level you want to have
        # otherwise your plant will never get water
        if just_stopped_adjusting:
            just_stopped_adjusting = False
            if options[1].optionValue > options[0].optionValue:
                options[1].optionValue = options[0].optionValue - 1

    # if the button has been pressed three seconds and the button is down now, start changing the option value
    if time.ticks_ms() > start_adjusting_value_counter and start_adjusting_value_counter != 0 and button.value() == 0 and not welcome_screen:
        adjust_option = True
        welcome_screen_counter = 0 # disable welcome screen counter
        if options[current_option].optionName != "PumpControl" and sleep_order == 0:
            options[current_option].optionValue += options[current_option].threshold # increase option value, except not with the pump on/off option
            if options[current_option].optionValue > options[current_option].max_value: # if the option value is now > max, set it to min
                options[current_option].optionValue = options[current_option].min_value
            if options[current_option].optionValue == 0 and options[current_option].optionName == "PumpRunTime":
                set_pump_run_time_to_1 = True
        if sleep_order == 0:
            sleep_order = 0.1

    # if you're adjusting the "pump on" option value, turn the pump on
    if adjust_option and options[current_option].optionName == "PumpControl":
        if pump_off_time == 0 and (time.ticks_ms() > pump_on_again_counter):
            options[current_option].optionValue = 1
            start_pump()
            if options[2].optionValue != 0:
                pump_off_time = time.ticks_ms() + options[2].optionValue*1000
            else: # if its set to "auto"
                pump_off_time = time.ticks_ms() + pump_run_time*1000
            pump_turned_on = True
            pump_on_again_counter = pump_off_time + 3000

    # stop adjusting the option value if the button is up
    if adjust_option and current_button_state == 1:
        adjust_option = False
        just_stopped_adjusting = True
        start_adjusting_value_counter = time.ticks_ms() + 3000
        welcome_screen_counter = time.ticks_ms() + 5000

    # check if it's time to show the welcome screen
    if time.ticks_ms() > welcome_screen_counter and welcome_screen_counter != 0:
        welcome_screen = True

    # check if the pump is off and the "pump off" text has to be written on OLED display
    if pump_off_time == 0 and options[current_option].optionName == "PumpControl" and not welcome_screen:
        fbuf.fill(0)
        fbuf.text(str(options[current_option].firstLine), 0, 8) # write the first line of the option text
        fbuf.text(str(options[current_option].secondLine), 0, 20) # write the second line of the option text
        fbuf.text(options[current_option].off_text, 50, 40) # write the "pump off" text
        draw_on_oled = True # tell the main function that something has to be drawn on the display now
    
    return [fbuf, options, current_button_state, current_option, welcome_screen, welcome_screen_opening_time, adjust_option, start_adjusting_value_counter, just_stopped_adjusting, pump_run_time, pump_on_again_counter, welcome_screen_counter, previous_button_state, sleep_order, draw_on_oled, pump_off_time, pump_turned_on, set_pump_run_time_to_1]


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
        return None

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
    return round(moisture_percent, 2)

# Function to store 24 soil moisture values into an array (if measured every 5 seconds, 24 values = 2 minutes)
def add_moisture_to_array(moisture_values, newest_value):
    moisture_values.append(newest_value)
    if len(moisture_values) > 24:
        moisture_values.pop(0)
    return moisture_values

# Function to calculate average of 24 soil moisture values
def get_moisture_2min_avg(moisture_values):
    if len(moisture_values) < 24: # if there is less measurements than 24, return zero
        return 0
    else:
        return sum(moisture_values) / len(moisture_values) # return average of 24 measurements

# Function to set the watering threshold value (after the user has changed it)
def set_threshold(desired_moisture_value, threshold_value):
    if threshold_value == 0: # 0 = auto
        return round(desired_moisture_value*0.9) # if you set threshold to "auto", it will set it to be 90 % of the desired moisture value
    else:
        return threshold_value

# Function to set the pump running time value (after the user has changed it)
def set_pump_run_time(pump_current_value, pump_user_setting, set_pump_run_time_to_1):
    if set_pump_run_time_to_1: # 0 = auto
        return 1.0 # if you set the pump running time to "auto", it will set it to 1.0
    elif pump_user_setting == 0:
        return pump_current_value
    else:
        return pump_user_setting


# Function to start the pump
def start_pump():
    print("START THE PUMP " + str(time.time()))
    # CODE HERE TO START THE PUMP!

# Function to stop the pump
def stop_pump():
    print("STOP THE PUMP " + str(time.time()))
    # CODE HERE TO STOP THE PUMP!


# Main
if __name__ == "__main__":
    
    oled.fill(0)
    oled.show()
    
    wlan = connect_wlan()
    mqtt_client = connect_mqtt()
    
    time.sleep(1)
    
    if mqtt_client is None:
        print("Unable to connect to MQTT")
        exit()

    plant_1_moisture = 1 # the desired moisture level for the plant, can be set
    plant_1_threshold = 9 # the threshold when the pump goes on
    pump_run_time = 0.5 # how long the pump will run
    pump_off_time = 0 # timestamp when the pump will be turned of automatically
    next_message_time = time.ticks_ms() + 5000 # timestamp when the next Mqtt message should be sent
    soil_moisture = 0 # measured soil moisture
    soil_moisture_2min_avg = 0 # measured 2 min average soil moisture (average of 24 values)
    moisture_values = [] # an array which contains soil moisture measurements (max. 24)
    moisture_change_measuring_time = 0 # timestamp when it will measure the moisture again after running the pump
    moisture_avg_after_pumping = 0 # the moisture value after running the pump
    set_pump_run_time_to_1 = False # if the user sets pump running time to "auto", it will set the time to 1.0

    while True:
        # if-elif-else is just to avoid that it wouldn't do too many things at same time (so it won't crash)
        
        # measuring and publishing the moisture every 5 seconds
        if time.ticks_ms() > next_message_time:
            soil_moisture = get_moisture()
            moisture_values = add_moisture_to_array(moisture_values, soil_moisture)
            soil_moisture_2min_avg = get_moisture_2min_avg(moisture_values)
            print("Settings: Moisture level: " + str(plant_1_moisture)+ ", Threshold: " + str(plant_1_threshold) + ", Pump run time: " + str(pump_run_time))
            
            next_message_time += 5000 # timestamp when the next Mqtt message should be sent
            publish_moisture(mqtt_client, soil_moisture)
            time.sleep(0.2)
            
            # if the plant needs to be watered - turn the pump on
            if soil_moisture_2min_avg < float(plant_1_threshold) and soil_moisture_2min_avg != 0:
                start_pump()
                pump_off_time = time.ticks_ms() + pump_run_time*1000
                pump_turned_on = True
        
        # check if the pump has to be turned off
        elif pump_off_time != 0 and time.ticks_ms() > pump_off_time:
            stop_pump()
            pump_off_time = 0
            options[3].optionValue = 0 # pump option value to 0 = off

        else:
            if welcome_screen: # showing the welcome screen (the picture of the plant or statistics)
                if welcome_screen_opening_time == 0: # if the welcome screen is now opened
                    welcome_screen_opening_time = time.ticks_ms() # take a timestamp
                    
                # set a time counter that goes from 0 to 19 (for welcome screen animations)
                time_state = round((time.ticks_ms() - welcome_screen_opening_time) / 1000) % 20
                # if time_state is between 0-9: show screen number 1, between 10-19: show screen number 2
                current_option = -1 # disable setting any option during welcome screen
                
                # draw welcome screen on fbuf
                fbuf.fill(0)
                fbuf = draw_welcome_screen(fbuf, time_state, soil_moisture, soil_moisture_2min_avg)
                draw_on_oled = True
            
            # draw options on fbuf
            # give all the option variables to function set_options()
            # it makes changes if needed and returns them back
            fbuf, options, current_button_state, current_option, welcome_screen, welcome_screen_opening_time, adjust_option, start_adjusting_value_counter, just_stopped_adjusting, pump_run_time, pump_on_again_counter, welcome_screen_counter, previous_button_state, sleep_order, draw_on_oled, pump_off_time, pump_turned_on, set_pump_run_time_to_1 = set_options(fbuf, options, button.value(), current_option, welcome_screen, welcome_screen_opening_time, adjust_option, start_adjusting_value_counter, just_stopped_adjusting, pump_run_time, pump_on_again_counter, welcome_screen_counter, previous_button_state, sleep_order, draw_on_oled, pump_off_time, pump_turned_on, set_pump_run_time_to_1)
            plant_1_moisture = options[0].optionValue
            plant_1_threshold = set_threshold(options[0].optionValue, options[1].optionValue)
            pump_run_time = set_pump_run_time(pump_run_time, options[2].optionValue, set_pump_run_time_to_1)
            set_pump_run_time_to_1 = False
            
            # if there is something in fbuf (welcome or options screen) that we need to draw on OLED display
            if draw_on_oled:
                try:
                    oled.fill(0)
                    oled.blit(fbuf, 0, 0, 0)
                    oled.show()
                    draw_on_oled = False
                except Exception: # sometimes sending MQTT message at the same time seems to give an exception
                    pass
            
            # if you have set some options, there might be a need to sleep for a moment (so that the button works correctly)
            if sleep_order > 0: 
                time.sleep(sleep_order)
                sleep_order = 0
        
        # if the pump is turned on, publish a mqtt message
        if pump_turned_on:
            publish_pump(mqtt_client, pump_run_time)
            if soil_moisture_2min_avg != 0 and moisture_change_measuring_time == 0 and options[2].optionValue == 0:
                moisture_change_measuring_time = time.ticks_ms() + pump_run_time*1000 + 120000
                print("Started auto adjusting the pump running time - wait for 2 minutes")
            elif moisture_change_measuring_time != 0:
                moisture_change_measuring_time = 0
                print("Stopped auto adjusting the pump running time")
            pump_turned_on = False
            
        if moisture_change_measuring_time != 0 and time.ticks_ms() > moisture_change_measuring_time:
            moisture_avg_after_pumping = soil_moisture_2min_avg
            print("The avg moisture after pumping was " +str(moisture_avg_after_pumping))
            if options[2].optionValue == 0 and moisture_avg_after_pumping > plant_1_moisture:
                pump_run_time -= 0.1 # auto adjust the pump running time
                print("It's higher than " + str(plant_1_moisture) + " so auto adjusting the pump running time to be 0.1 seconds shorter")
            elif options[2].optionValue == 0 and moisture_avg_after_pumping < plant_1_moisture:
                pump_run_time += 0.1 # auto adjust the pump running time
                print("It's lower than " + str(plant_1_moisture) + " so auto adjusting the pump running time to be 0.1 seconds longer")
            moisture_change_measuring_time = 0
        
        time.sleep(0.01)
