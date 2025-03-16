import requests
import csv
from tqdm import tqdm

def fetch_pokemon_data():
    base_url = "https://pokeapi.co/api/v2/pokemon/"
    species_url = "https://pokeapi.co/api/v2/pokemon-species/"
    
    # Get the total number of Pokémon
    response = requests.get(base_url + "?limit=1")
    total_pokemon = response.json()["count"]
    
    data = []
    
    for pokemon_id in tqdm(range(1, total_pokemon + 1)):
        pokemon_response = requests.get(base_url + str(pokemon_id))
        species_response = requests.get(species_url + str(pokemon_id))
        
        if pokemon_response.status_code != 200 or species_response.status_code != 200:
            print(f"Skipping Pokémon ID {pokemon_id} due to fetch error.")
            continue
        
        pokemon_data = pokemon_response.json()
        species_data = species_response.json()
        
        name = pokemon_data["name"]
        types = ", ".join([t["type"]["name"] for t in pokemon_data["types"]])
        abilities = ", ".join([a["ability"]["name"] for a in pokemon_data["abilities"]])
        height = pokemon_data["height"]
        weight = pokemon_data["weight"]
        base_experience = pokemon_data.get("base_experience", 0)
        
        # Fetching the flavor text from species data (English only)
        flavor_text_entries = species_data["flavor_text_entries"]
        flavor_text = next((entry["flavor_text"].replace("\n", " ").replace("\f", " ")
                            for entry in flavor_text_entries if entry["language"]["name"] == "en"), "No description available.")
        
        data.append([name, types, abilities, height, weight, base_experience, flavor_text])
    
    # Write to CSV
    with open("pokemon_data.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Types", "Abilities", "Height", "Weight", "Base Experience", "Flavor Text"])
        writer.writerows(data)
    
    print("CSV file 'pokemon_data.csv' has been created successfully.")

# Run the function
fetch_pokemon_data()
