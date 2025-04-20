import network
from time import sleep
import urequests
import json

# Replace these values with your own
SSID = "SmartIoTMQTT"
PASSWORD = "SmartIot"
BROKER_IP = "192.168.1.254"

# Function to connect to WLAN
def connect_wlan():
    # Connecting to the group WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    # Attempt to connect once per second
    while wlan.isconnected() == False:
        print("Connecting... ")
        sleep(1)

    # Print the IP address of the Pico
    print("Connection successful. Pico IP:", wlan.ifconfig()[0])
    
# Main program
if __name__ == "__main__":
    #Connect to WLAN
    connect_wlan()
    while True:
        pokemon_id = input("Please give Pokemon ID: ")
        try:
            if int(pokemon_id) >= 1 and int(pokemon_id) <= 1025:
                url = "https://pokeapi.co/api/v2/pokemon-species/" + pokemon_id
                response = urequests.get(url)
                json_data = json.loads(response.text)
                print("The name of the pokemon is " + json_data["name"])
                del json_data # deleting the variable to save memory
            else:
                print("Please give a number between 1 and 1025.")
        except Exception as e:
            print(f"Failed {e}")

