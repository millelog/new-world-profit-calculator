#database/init_db.py

import requests
import yaml
from sqlalchemy import create_engine
from config.database_config import DATABASE_URI
from database.models import (Base, Item, CraftingRecipe, RecipeReagent, TradeSkill,
                             Player, PlayerSkill, Transaction, Server, RecipeSkillRequirement, item_itemtype_association, ItemType)
from sqlalchemy.orm import sessionmaker
import os
import json

DATABASE_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def load_yaml(filename):
    """Helper function to load YAML data from a file."""
    with open(filename, 'r') as file:
        return yaml.safe_load(file)


def load_json(filename):
    """Helper function to load JSON data from a file."""
    with open(filename, 'r') as file:
        return json.load(file)

def load_servers(session):
    servers = load_json(os.path.join(DATABASE_DATA_DIR, 'servers.json'))
    for server in servers:
        if not session.query(Server).filter_by(server_name=server["server_name"]).first():
            session.add(Server(**server))


def load_trade_skills(session):
    trade_skills = load_json(os.path.join(DATABASE_DATA_DIR, 'trade_skills.json'))
    for skill in trade_skills:
        if not session.query(TradeSkill).filter_by(skill_name=skill["skill_name"]).first():
            session.add(TradeSkill(**skill))


def load_players(session):
    players = load_json(os.path.join(DATABASE_DATA_DIR, 'players.json'))
    for player_data in players:
        player_name = player_data["player_name"]
        server_name = player_data["server_name"]
        server = session.query(Server).filter_by(server_name=server_name).first()
        if not session.query(Player).filter_by(player_name=player_name, server_id=server.server_id).first():
            player = Player(player_name=player_name, server_id=server.server_id)
            session.add(player)
            session.flush()
            for skill in player_data["skills"]:
                skill_entry = session.query(TradeSkill).filter_by(skill_name=skill["skill_name"]).first()
                session.add(PlayerSkill(player_id=player.player_id, skill_id=skill_entry.skill_id, skill_level=skill["skill_level"]))


def load_items(session):
    """
    Fetch item data from the API, save it to a JSON file, and then load the items to the database.
    If an item already exists, its fields are updated.
    """
    # First, fetch the item data and save it to a JSON file
    fetch_and_save_item_names()

    # Define the static path to the saved JSON file
    filename = os.path.join(DATABASE_DATA_DIR, 'nw_marketprices_item_names.json')

    # Load the item data from the JSON file
    with open(filename, 'r') as file:
        item_data = json.load(file)
    
    # Iterate over each item entry and either update or insert into the database
    for item, details in item_data.items():
        # Query the database for an existing item with the same ID
        existing_item = session.query(Item).filter_by(item_id=details["nwdb_id"]).first()
        
        # If the item doesn't already exist in the database, create it
        if not existing_item:
            new_item = Item(
                item_id=details["nwdb_id"],
                item_name=details["name"],
                nw_market_id=details["name_id"]
            )
            session.add(new_item)
        else:
            # If the item already exists, update its fields
            existing_item.item_name = details["name"]
            existing_item.nw_market_id = details["name_id"]

    # Commit the changes to the database
    session.commit()

def fetch_and_save_item_names():
    # Define the API endpoint and output file path
    api_url = "https://nwmarketprices.com/api/confirmed_names/"
    output_file_path = os.path.join(DATABASE_DATA_DIR, 'nw_marketprices_item_names.json')
    
    # Check if the file already exists
    if os.path.exists(output_file_path):
        print(f"File {output_file_path} already exists. Skipping download.")
        return

    # Make a request to the API
    response = requests.get(api_url)
    
    # Check if the request was successful
    if response.status_code == 200:
        with open(output_file_path, 'w') as file:
            json.dump(response.json(), file)
        print(f"Item names saved to {output_file_path}")
    else:
        print(f"Error fetching item names from {api_url}. HTTP Status Code: {response.status_code}")


def load_crafting_categories(session):
    category_data = load_yaml(os.path.join(DATABASE_DATA_DIR, 'CraftingCategory.json'))
    
    for category, details in category_data.items():
        # Use category (key from the JSON) as the item type name
        item_type = session.query(ItemType).filter_by(item_type_name=category).first()
        
        # If not, add it
        if not item_type:
            item_type = ItemType(item_type_name=category)
            session.add(item_type)
            session.flush()  # So that we can get the item_type_id

        # Check if the items for this category exist and if not, add them
        for item_id in details.get("options", []):
            item = session.query(Item).filter_by(item_id=item_id).first()
            if not item:
                # If the specific item details are in category_data, we can get its name
                item_name = category_data.get(item_id, {}).get("name", "")
                item = Item(item_id=item_id, item_name=item_name)
                session.add(item)
                
            # Add the item type association for this item
            if not session.query(item_itemtype_association).filter_by(item_id=item.item_id, item_type_id=item_type.item_type_id).first():
                association = {
                    'item_id': item.item_id,
                    'item_type_id': item_type.item_type_id
                }
                session.execute(item_itemtype_association.insert().values(**association))

    session.commit()


def load_recipes(session):
    recipes = load_yaml(os.path.join(DATABASE_DATA_DIR, 'CraftingRecipes.yml'))
    for recipe_data in recipes:
        result_item = session.query(Item).filter_by(item_id=recipe_data["ItemID"].lower()).first()
        if result_item:
            if not session.query(CraftingRecipe).filter_by(result_item_id=result_item.item_id).first():
                recipe = CraftingRecipe(result_item_id=result_item.item_id, quantity_produced=recipe_data["OutputQty"])
                session.add(recipe)
                session.flush()

                # Populate RecipeSkillRequirement table
                trade_skill = session.query(TradeSkill).filter_by(skill_name=recipe_data["Tradeskill"]).first()
                if trade_skill:
                    skill_requirement = RecipeSkillRequirement(
                        recipe_id=recipe.recipe_id,
                        skill_id=trade_skill.skill_id,
                        level_required=recipe_data["RecipeLevel"]
                    )
                    session.add(skill_requirement)

                for idx in range(1, 8):  # Assuming up to 7 ingredients based on provided data
                    ingredient_name = recipe_data[f"Ingredient{idx}"].lower()
                    ingredient_qty = recipe_data[f"Qty{idx}"]
                    ingredient_type = recipe_data[f"Type{idx}"]

                    if ingredient_name and ingredient_qty:
                        if ingredient_type == "Category_Only":
                            # Here, instead of an item_id, we set item_type
                            ingredient_item_type = session.query(ItemType).filter_by(item_type_name=ingredient_name).first()
                            if ingredient_item_type:
                                session.add(RecipeReagent(
                                    recipe_id=recipe.recipe_id,
                                    reagent_item_type_id=ingredient_item_type.item_type_id,
                                    quantity_required=ingredient_qty
                                ))
                        else:
                            ingredient_item = session.query(Item).filter_by(item_id=ingredient_name).first()
                            if ingredient_item:
                                session.add(RecipeReagent(
                                    recipe_id=recipe.recipe_id,
                                    reagent_item_id=ingredient_item.item_id,
                                    quantity_required=ingredient_qty
                                ))
        else:
            print(f"Item {recipe_data['ItemID']} not found in database.")
    
    session.commit()

def init_data(session):
    load_servers(session)
    load_trade_skills(session)
    load_players(session)
    load_crafting_categories(session)
    load_items(session)
    load_recipes(session)
    
    session.commit()
    print("Static data initialized successfully!")


def init_database():
    """Initialize the SQLite database with the required tables."""
    engine = create_engine(DATABASE_URI)
    Base.metadata.create_all(engine)
    print("Database initialized successfully!")

    # Now, initiate a session and populate data after creating tables
    Session = sessionmaker(bind=engine)
    session = Session()
    init_data(session)

if __name__ == "__main__":
    init_database()
