from sqlalchemy import create_engine
from config.database_config import DATABASE_URI
from database.models import (Base, Item, CraftingRecipe, RecipeReagent, TradeSkill,
                             Player, PlayerSkill, Transaction, Server, RecipeSkillRequirement)
from sqlalchemy.orm import sessionmaker
import os
import json

DATABASE_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

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


def load_tracked_items(session):
    tracked_items = load_json(os.path.join(DATABASE_DATA_DIR, 'tracked_items.json'))
    for item in tracked_items:
        if not session.query(Item).filter_by(item_id=item["item_id"]).first():
            session.add(Item(**item))


def load_recipes(session):
    recipe_category_dir = os.path.join(DATABASE_DATA_DIR, 'recipes')
    for category_file in os.listdir(recipe_category_dir):
        if category_file.endswith(".json"):
            recipes = load_json(os.path.join(recipe_category_dir, category_file))
            for recipe_data in recipes:
                if not session.query(CraftingRecipe).filter_by(result_item_id=recipe_data["result_item_id"]).first():
                    recipe = CraftingRecipe(result_item_id=recipe_data["result_item_id"], quantity_produced=recipe_data["quantity_produced"])
                    session.add(recipe)
                    session.flush()
                    
                    for reagent in recipe_data["reagents"]:
                        if not session.query(RecipeReagent).filter_by(recipe_id=recipe.recipe_id, reagent_item_id=reagent["item_id"]).first():
                            session.add(RecipeReagent(recipe_id=recipe.recipe_id, reagent_item_id=reagent["item_id"], quantity_required=reagent["quantity_required"]))
                    
                    for skill_req in recipe_data["skills_required"]:
                        skill = session.query(TradeSkill).filter_by(skill_name=skill_req["skill_name"]).first()
                        if skill and not session.query(RecipeSkillRequirement).filter_by(recipe_id=recipe.recipe_id, skill_id=skill.skill_id).first():
                            session.add(RecipeSkillRequirement(recipe_id=recipe.recipe_id, skill_id=skill.skill_id, level_required=skill_req["level_required"]))


def init_data(session):
    load_servers(session)
    load_trade_skills(session)
    load_players(session)
    load_tracked_items(session)
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
