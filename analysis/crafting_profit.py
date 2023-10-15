from database.models import CraftingRecipe
import  database.operations.current_price_operations as cpo
import database.operations.recipe_operations as ro
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config.database_config import DATABASE_URI

# Initialize DB session
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def get_crafting_cost(session, recipe, crafting_tree=None):
    """
    Recursively calculate the total crafting cost for a given recipe.
    This includes the cost of crafting or buying all reagents.
    """
    if crafting_tree is None:
        crafting_tree = {}  # Initialize crafting tree
    
    total_cost = 0
    for reagent in recipe.recipe_reagents:
        reagent_item_id = reagent.reagent_item_id
        reagent_quantity = reagent.quantity_required
        
        # If this reagent has already been evaluated in this crafting tree, use the known cost
        if reagent_item_id in crafting_tree:
            total_cost += crafting_tree[reagent_item_id]['cost'] * reagent_quantity
            continue
        
        # Get reagent market price
        market_price_data = cpo.get_current_price(session, reagent_item_id)
        market_price = market_price_data['price'] if market_price_data else float('inf')  # Assume infinite cost if no market price data
        
        # If the reagent has crafting recipes, calculate the crafting cost
        reagent_recipes = ro.get_recipes_by_item(session, reagent_item_id)
        if reagent_recipes:
            crafting_options = []  # List to store crafting options and their costs
            for reagent_recipe in reagent_recipes:
                # Recursive call to evaluate the cost of crafting this reagent
                reagent_crafting_cost, reagent_crafting_tree = get_crafting_cost(session, reagent_recipe, crafting_tree)
                crafting_options.append((reagent_crafting_cost, reagent_crafting_tree))
            
            # Choose the cheapest crafting option
            crafting_cost, crafting_option_tree = min(crafting_options, key=lambda x: x[0])
            crafting_tree.update(crafting_option_tree)  # Update the crafting tree with the chosen option
        else:
            crafting_cost = market_price  # No crafting recipes, must buy from market
        
        # Store this reagent's cost in the crafting tree
        crafting_tree[reagent_item_id] = {
            'cost': crafting_cost,
            'source': 'crafted' if reagent_recipes and crafting_cost < market_price else 'market'
        }
        
        # Accumulate the cost
        total_cost += crafting_cost * reagent_quantity
    
    # Include the crafting fee if any (assumed to be 0 for simplicity)
    crafting_fee = 0
    total_cost += crafting_fee

    return total_cost, crafting_tree


def calculate_profitability(session, item_id):
    """
    Calculate the profitability of crafting an item.
    Returns the profit margin and the recommended crafting path.
    """
    recipes = ro.get_recipes_by_item(session, item_id)
    if not recipes:
        raise ValueError(f"No recipes found for item {item_id}")
    
    market_price_data = cpo.get_current_price(session, item_id)
    market_price = market_price_data['price'] if market_price_data else float('inf')  # Assume infinite price if no market data
    
    # Find the most profitable recipe
    max_profit_margin = float('-inf')
    recommended_recipe = None
    recommended_crafting_tree = None
    for recipe in recipes:
        crafting_cost, crafting_tree = get_crafting_cost(session, recipe)
        profit_margin = market_price - crafting_cost
        if profit_margin > max_profit_margin:
            max_profit_margin = profit_margin
            recommended_crafting_tree = crafting_tree
    
    return max_profit_margin, recommended_recipe, recommended_crafting_tree



def evaluate_all_recipes(session):
    """
    Evaluate the profitability of crafting every recipe in the database.
    """
    # Query all crafting recipes
    all_recipes = session.query(CraftingRecipe).all()
    
    # Dictionary to store profitability information for each recipe
    profitability_info = {}
    
    for recipe in all_recipes:
        item_id = recipe.result_item_id
        profit_margin, recommended_recipe, crafting_tree = calculate_profitability(session, item_id)
        profitability_info[item_id] = {
            "Profit Margin": profit_margin,
            "Recommended Recipe ID": recommended_recipe.recipe_id if recommended_recipe else None,
            "Crafting Tree": crafting_tree
        }
    
    return profitability_info


if __name__ == "__main__":
    item_id = 'essenceairt1'
    profit_margin, recommended_recipe = calculate_profitability(session, item_id)
    print(f"Profit Margin: {profit_margin}")
    print(f"Recommended Recipe ID: {recommended_recipe.recipe_id}")

