import os
import json
import glob

# Define the base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define the path to the tracked items file
TRACKED_ITEMS_PATH = os.path.join(BASE_DIR, 'database', 'data', 'tracked_items.json')

# Define the path to the download data file
DOWNLOAD_DATA_PATH = os.path.join(BASE_DIR, 'download.json')

# Define the path to the recipes directory
RECIPES_DIR = os.path.join(BASE_DIR, 'database', 'data', 'recipes')

def get_tracked_items():
    with open(TRACKED_ITEMS_PATH, 'r') as file:
        return json.load(file)

def get_download_data():
    with open(DOWNLOAD_DATA_PATH, 'r') as file:
        return json.load(file)

def update_tracked_items(tracked_items):
    with open(TRACKED_ITEMS_PATH, 'w') as file:
        json.dump(tracked_items, file, indent=4)

def main():
    # Load existing tracked items and download data
    tracked_items = get_tracked_items()
    download_data = get_download_data()

    # Create a dictionary to map item names to item IDs from download data
    item_name_to_id = {item['ItemName']: item['ItemId'] for item in download_data}

    # Gather all recipe JSON files from the recipes directory
    recipe_files = glob.glob(f"{RECIPES_DIR}/*.json")

    for recipe_file in recipe_files:
        with open(recipe_file, 'r') as file:
            recipes = json.load(file)

        for recipe in recipes:
            for ingredient in recipe['ingredients']:
                # Check if the ingredient is an item type
                if 'item_type' in ingredient:
                    continue

                ingredient_name = ingredient['ingredient_name']
                
                # Check if the ingredient is already in tracked items
                if not any(item['item_name'] == ingredient_name for item in tracked_items):
                    # Look up the item_id from download data
                    item_id = item_name_to_id.get(ingredient_name)
                    if item_id:
                        # Add the new ingredient to tracked items
                        tracked_items.append({'item_id': item_id, 'item_name': ingredient_name})

    # Update the tracked items file with any new ingredients
    update_tracked_items(tracked_items)

if __name__ == '__main__':
    main()
