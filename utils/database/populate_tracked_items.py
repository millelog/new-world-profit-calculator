import json
import re
import os

# Adjust BASE_DIR to reflect that this script is two directories deep from the root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Construct the full paths to JSON files
tracked_item_names_path = os.path.join(BASE_DIR, 'utils/database/tracked_item_names.json')
download_data_path = os.path.join(BASE_DIR, 'download.json')
tracked_items_path = os.path.join(BASE_DIR, 'database/data/tracked_items.json')

# Load item names to be tracked
with open(tracked_item_names_path, 'r') as file:
    tracked_item_names = json.load(file)

# Load the data to map item names to IDs
with open(download_data_path, 'r') as file:
    all_items_data = json.load(file)

# Prepare the tracked_items list based on the names
tracked_items = []

for item_name_pattern in tracked_item_names:
    # Compile the regex pattern
    pattern = re.compile(item_name_pattern)

    # Find matching items in all_items_data based on the regex pattern
    matching_items = [item for item in all_items_data if pattern.match(item["ItemName"])]

    # Add matched items to the tracked_items list
    for matching_data in matching_items:
        # Check if the item_id is already in the tracked_items list
        if not any(item["item_id"] == matching_data["ItemId"] for item in tracked_items):
            tracked_items.append({
                "item_id": matching_data["ItemId"],
                "item_name": matching_data["ItemName"]
            })


# Save the tracked items
with open(tracked_items_path, 'w') as file:
    json.dump(tracked_items, file, indent=4)
