import os
import time
import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://nwdb.info/db/recipe/"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        return None

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extracting the recipe name
    recipe_name = soup.select_one('.item-name h1').text.strip().split(":")[1].strip()

    # Extracting category
    category = soup.select_one('.item-name span.d-flex span').text.strip().replace(' ', '_').lower()

    # Extracting the skill requirement
    skill_elements = soup.select('span.stat-name:contains("Requires") + span.stat-value')
    skills_required = []
    for elem in skill_elements:
        skill_text = elem.text.strip()
        if "Skill" in skill_text:
            skill_parts = skill_text.split('Lv. ')
            if len(skill_parts) == 2:
                skills_required.append({
                    'skill_name': skill_parts[0].strip(),
                    'level_required': int(skill_parts[1])
                })

    # Extracting ingredients
    ingredients_sections = soup.select('.my-3.ps-2')
    ingredients = []

    for section in ingredients_sections:
        quantity_elem = section.select_one('span.text-white')
        if quantity_elem:
            quantity = quantity_elem.text.strip().replace('x', '')
            ingredient_name_elem = section.select_one('.ps-1')
            nested_div = section.select_one('.mt-1.ms-5')
            if nested_div:
                item_type_elem = section.select_one('.fw-bold:not(.text-white)')
                if item_type_elem:
                    item_type = item_type_elem.text.strip()
                    ingredients.append({
                        'quantity': quantity,
                        'item_type': item_type
                    })
            elif ingredient_name_elem:
                ingredient_name = ingredient_name_elem.text.strip()
                ingredients.append({
                    'quantity': quantity,
                    'ingredient_name': ingredient_name
                })

    # Extracting craft amount
    crafted_item_section = soup.select_one('.my-3')
    if crafted_item_section:
        craft_amount_elem = crafted_item_section.select_one('span.text-white')
        craft_amount = int(craft_amount_elem.text.strip().replace('x', '')) if craft_amount_elem else None
    else:
        craft_amount = None

    return {
        'recipe_name': recipe_name,
        'skills_required': skills_required,
        'ingredients': ingredients,
        'category': category,
        'craft_amount': craft_amount
    }

def fetch_and_save_data(tracked_items):
    recipes = []
    for item in tracked_items:
        item_id = item['item_id']
        html_content = fetch_html(item_id)
        recipe_data = extract_data_from_html(html_content)
        print(recipe_data)
        if recipe_data is None:
            continue
        
        recipes.append(recipe_data)
        category_file_path = os.path.join(BASE_DIR, 'database', 'data', 'recipes', f"{recipe_data['category']}.json")
        
        # Append to the existing JSON file for the specific category
        if os.path.exists(category_file_path):
            with open(category_file_path, 'r') as f:
                existing_data = json.load(f)
            existing_data.append(recipe_data)
            with open(category_file_path, 'w') as f:
                json.dump(existing_data, f, indent=4)
        else:
            # Create new category file if it doesn't exist
            with open(category_file_path, 'w') as f:
                json.dump([recipe_data], f, indent=4)



if __name__ == "__main__":
    tracked_items_path = os.path.join(BASE_DIR, 'database', 'data', 'tracked_items.json')
    with open(tracked_items_path, 'r') as f:
        tracked_items = json.load(f)

    # Assuming tracked_items.json is a list of item_ids
    fetch_and_save_data(tracked_items)
