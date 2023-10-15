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

def get_crafting_cost(session, recipe, server_id, crafting_tree=None):
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
        market_price_data = cpo.get_current_price(session, reagent_item_id, server_id)
        market_price = market_price_data['price'] if market_price_data else float('inf')  # Assume infinite cost if no market price data

        # If the reagent has crafting recipes, calculate the crafting cost
        reagent_recipes = ro.get_recipes_by_item(session, reagent_item_id)
        if reagent_recipes:
            crafting_options = []  # List to store crafting options and their costs
            for reagent_recipe in reagent_recipes:
                # Recursive call to evaluate the cost of crafting this reagent
                reagent_crafting_cost, reagent_crafting_tree = get_crafting_cost(session, reagent_recipe, server_id, {})
                crafting_options.append((reagent_crafting_cost, reagent_crafting_tree))

            # Choose the cheapest crafting option
            crafting_cost, crafting_option_tree = min(crafting_options, key=lambda x: x[0])

            # Store this reagent's cost, quantity, and crafting tree in the current crafting tree
            crafting_tree[reagent_item_id] = {
                'cost': crafting_cost,
                'quantity': reagent_quantity,
                'source': 'crafted' if reagent_recipes and crafting_cost < market_price else 'market',
                'children': crafting_option_tree  # Include the crafting tree for this reagent as a child
            }
        else:
            crafting_cost = market_price  # No crafting recipes, must buy from market
            crafting_tree[reagent_item_id] = {
                'cost': crafting_cost,
                'quantity': reagent_quantity,
                'source': 'market'
            }

        # Accumulate the cost
        total_cost += crafting_cost * reagent_quantity

    # Include the crafting fee if any (assumed to be 0 for simplicity)
    crafting_fee = 0
    total_cost += crafting_fee

    return total_cost, crafting_tree



def calculate_profitability(session, item_id, server_id):
    recipes = ro.get_recipes_by_item(session, item_id)
    if not recipes:
        raise ValueError(f"No recipes found for item {item_id}")

    market_price_data = cpo.get_current_price(session, item_id, server_id)
    market_price = market_price_data['price'] if market_price_data else float('inf')  # Assume infinite price if no market data

    max_score = float('-inf')
    recommended_recipe = None
    recommended_crafting_tree = None
    max_profit_margin = float('-inf')  # Initialize with negative infinity
    max_profit_margin_percentage = float('-inf')  # Initialize with negative infinity

    for recipe in recipes:
        crafting_cost, crafting_tree = get_crafting_cost(session, recipe, server_id)
        if crafting_cost == 0:
            continue  # Avoid division by zero

        profit_margin = market_price - crafting_cost
        profit_margin_percentage = (profit_margin / crafting_cost) * 100 if crafting_cost != 0 else 0
        availability = market_price_data['availability'] if market_price_data else 0
        score = calculate_score(profit_margin_percentage, profit_margin, availability)

        if score > max_score:
            max_score = score
            recommended_recipe = recipe
            recommended_crafting_tree = crafting_tree
            max_profit_margin = profit_margin  # Update max profit margin
            max_profit_margin_percentage = profit_margin_percentage  # Update max profit margin percentage

    return (
        max_score,
        recommended_recipe,
        recommended_crafting_tree,
        max_profit_margin,
        max_profit_margin_percentage,
        crafting_cost,
        market_price_data['qty'] if market_price_data and market_price_data['qty'] else (market_price_data['availability'] if market_price_data else None)
    )


def calculate_score(profit_margin_percentage, profit_margin, availability):
    if profit_margin_percentage < 0:
        return 0
    
    profit_margin_weight = 0  # for example, adjust as needed
    profit_weight = 1  # for example, adjust as needed
    availability_weight = 0  # for example, adjust as needed
    return profit_margin_weight * profit_margin_percentage + availability_weight * availability + profit_margin*profit_weight

def evaluate_all_recipes(session, server_id):
    all_recipes = session.query(CraftingRecipe).all()
    profitability_info = {}

    for recipe in all_recipes:
        item_id = recipe.result_item_id
        score, recommended_recipe, crafting_tree, profit_margin, profit_margin_percentage, crafting_cost, availability = calculate_profitability(session, item_id, server_id)
        profitability_info[item_id] = {
            "Score": score,
            "Recommended Recipe ID": recommended_recipe.recipe_id if recommended_recipe else None,
            "Crafting Tree": crafting_tree,
            "Profit Margin": profit_margin,
            "Profit Margin Percentage": profit_margin_percentage,
            "Crafting Cost": crafting_cost,
            "Availability": availability
        }

    # Sort items by score and get the top 50
    top_50_items = sorted(profitability_info.items(), key=lambda x: x[1]["Score"], reverse=True)[:50]

    return top_50_items



if __name__ == "__main__":
    item_id = 'essenceairt1'
    profit_margin, recommended_recipe = calculate_profitability(session, item_id)
    print(f"Profit Margin: {profit_margin}")
    print(f"Recommended Recipe ID: {recommended_recipe.recipe_id}")

