import argparse
import os
import time
import requests
import json
import openai


# OpenAI setup
openai.api_key = "YOUR_OPENAI_API_KEY"
GPT_MODEL = "gpt-4.0-turbo"

BASE_URL = "https://nwdb.info/db/recipe/"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import recipe operations
from database.operations.recipe_operations import add_recipe

functions = [
    {
        "name": "add_recipe",
        "description": "Add a new crafting recipe to the database",
        "parameters": {
            "type": "object",
            "properties": {
                "session": {
                    "type": "object",
                    "description": "The database session object"
                },
                "recipe_data": {
                    "type": "object",
                    "properties": {
                        "result_item_id": {
                            "type": "string",
                            "description": "ID of the item that results from the recipe"
                        },
                        "quantity_produced": {
                            "type": "integer",
                            "description": "Quantity of the result item produced by the recipe"
                        },
                        "reagents": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "item_id": {
                                        "type": "string",
                                        "description": "ID of the reagent item, if specified"
                                    },
                                    "item_type": {
                                        "type": "string",
                                        "description": "Type of the reagent item, if specified"
                                    },
                                    "quantity_required": {
                                        "type": "integer",
                                        "description": "Quantity of the reagent required for the recipe"
                                    }
                                },
                                "required": ["quantity_required"]
                            },
                            "description": "List of reagents required for the recipe"
                        }
                    },
                    "required": ["result_item_id", "quantity_produced", "reagents"]
                }
            },
            "required": ["session", "recipe_data"]
        }
    }
]


def fetch_html(item_id):
    url = BASE_URL + item_id
    print(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    }
    time.sleep(3)
    response = requests.get(url, headers=headers)
    print(response)
    return response.text

def parse_html_with_gpt(html_content):
    messages = []
    messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
    messages.append({"role": "user", "content": f"Parse the following HTML content and extract recipe data: {html_content}"})
    chat_response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=messages,
        functions=functions
    )
    parsed_data = chat_response.choices[0].message["content"]
    recipe_data = json.loads(parsed_data)
    return recipe_data

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--start-from', dest='start_from', help='Item ID to start processing from')
    return parser.parse_args()

def fetch_and_save_data(tracked_items, start_from=None):
    start_processing = start_from is None
    recipes = []
    for item in tracked_items:
        item_id = item['item_id']
        if not start_processing:
            if item_id == start_from:
                start_processing = True
            continue

        html_content = fetch_html(item_id)
        recipe_data = parse_html_with_gpt(html_content)
        print(recipe_data)
        if recipe_data is None:
            continue
        
        recipes.append(recipe_data)
        # Adding the parsed recipe to the database
        #with recipe_operations.session_scope() as session:
            #add_recipe(session, recipe_data)

def main():
    args = parse_arguments()
    tracked_items_path = os.path.join(BASE_DIR, 'database', 'data', 'tracked_items.json')
    with open(tracked_items_path, 'r') as f:
        tracked_items = json.load(f)
    fetch_and_save_data(tracked_items, start_from=args.start_from)

if __name__ == "__main__":
    main()
