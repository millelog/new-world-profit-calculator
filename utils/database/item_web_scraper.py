import os
import time
import requests
from bs4 import BeautifulSoup
import json
import argparse


BASE_URL = "https://nwdb.info/db/item/"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define the argument
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--start_from', type=str, help='Item ID to start processing from')
args = parser.parse_args()

def fetch_html(item_id):
    url = BASE_URL + item_id
    print(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    }
    time.sleep(5)
    response = requests.get(url, headers=headers)
    print(response)
    
    # Create a BeautifulSoup object and specify the parser
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the div with class 'panel-item-details'
    panel_item_details = soup.find('div', class_='panel-item-details')
    
    if panel_item_details:
        return panel_item_details.prettify()  # or .prettify() if you want the content in HTML format
    else:
        return None

def extract_data_from_html(html_content):
    if html_content is None:
        return None, None

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Locate the span element containing the ingredient types
    ingredient_types_elem = soup.select_one('.stats-container .stat-name:contains("Ingredient Types:") + .stat-value')
    if ingredient_types_elem:
        # Get the text content, split on comma, and strip whitespace from each item
        ingredient_types = [item.strip() for item in ingredient_types_elem.text.split(',')]
    else:
        ingredient_types = None

    # Locate the h1 element containing the item's name
    item_name_elem = soup.select_one('h1.h5')
    if item_name_elem:
        item_name = item_name_elem.text.strip()
    else:
        item_name = None
    
    return ingredient_types, item_name

def fetch_and_save_data(tracked_items, start_from=None):
    start = False
    for item in tracked_items:
        item_id = item['item_id']
        if start_from is None or start:
            html_content = fetch_html(item_id)
            ingredient_types, item_name = extract_data_from_html(html_content)
            print(ingredient_types, item_name)
            if ingredient_types is not None:
                item['item_type'] = ingredient_types
            if item_name is not None:
                item['item_name'] = item_name
        elif item_id == start_from:
            start = True  # Set start to True when the specified item_id is found

    tracked_items_path = os.path.join(BASE_DIR, 'database', 'data', 'tracked_items.json')
    # Save the updated tracked_items list back to tracked_items.json
    with open(tracked_items_path, 'w') as f:
        json.dump(tracked_items, f, indent=4)

if __name__ == "__main__":
    tracked_items_path = os.path.join(BASE_DIR, 'database', 'data', 'tracked_items.json')
    with open(tracked_items_path, 'r') as f:
        tracked_items = json.load(f)

    # Pass the argument to your function
    fetch_and_save_data(tracked_items, args.start_from)
