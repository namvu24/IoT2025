import requests


pokemon_id = int(input("Enter Pokémon ID number (1-1025): "))


if pokemon_id < 1 or pokemon_id > 1025:
    print("Invalid ID. Please enter a number between 1 and 1025.")
else:
    # Fetch the Pokémon name from PokéAPI
    url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}/"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        pokemon_name = data["name"]  
        print(f"The Pokémon with ID {pokemon_id} is {pokemon_name}.") 
    else:
        print(f"Could not fetch data for Pokémon ID {pokemon_id}. Please try again.")
