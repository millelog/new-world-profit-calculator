#analysis/crafting_profit.py

from database.models import CraftingRecipe
import database.operations.current_price_operations as cpo
import database.operations.recipe_operations as ro
import database.operations.player_operations as po
import database.operations.item_operations as io

MAX_DEPTH=10

def calculate_item_cost(session, item_id, server_id, player_id, depth=0):
    """
    Calculates the cost of an item either by crafting or market price.
    """
    if depth > MAX_DEPTH:
        # Return market price or some default value
        market_price_data = cpo.get_current_price(session, item_id, server_id)
        market_price = market_price_data['price'] if market_price_data else float('inf')
        return market_price, {}

    # Fetch potential crafting recipes for the item
    recipes = ro.get_recipes_by_item(session, item_id)

    # Fetch the market price for the item
    market_price_data = cpo.get_current_price(session, item_id, server_id)
    market_price = market_price_data['price'] if market_price_data else float('inf')

    # If no crafting recipes, default to market price
    if not recipes:
        return market_price, {}

    # If recipes exist, determine the cheapest method
    crafting_options = [
        get_crafting_cost(session, recipe, server_id, player_id, depth)
        for recipe in recipes
    ]
    min_crafting_cost = min(crafting_options, key=lambda x: x[0])[0]

    # Compare market price with crafting cost and return the cheaper option
    if market_price <= min_crafting_cost:
        return market_price, {}
    else:
        return min(crafting_options, key=lambda x: x[0])




def get_reagent_item_id(session, reagent, used_reagents, server_id):
    """
    Determines the reagent item ID for crafting, prioritizing specific item IDs or selecting from available item types.
    """
    if reagent.reagent_item_id:
        return reagent.reagent_item_id
    potential_items = io.get_items_for_item_type(session, reagent.reagent_item_type_id, server_id) #returns sorted by market price
    potential_items = [item for item in potential_items if item.item_id not in used_reagents]  # Filter out already used reagents
    if not potential_items:
        return None  # No valid items to use for this reagent
    # Assuming potential_items is sorted by price, return cheapest
    return potential_items[0].item_id


def get_crafting_cost(session, recipe, server_id, player_id, depth=0):
    """
    Calculates the crafting cost of a given recipe.
    """
    # Check if the player can craft the given recipe
    can_craft = po.can_craft_recipe(session, player_id, recipe.recipe_id)
    if not can_craft:
        market_price_data = cpo.get_current_price(session, recipe.result_item_id, server_id)
        market_price = market_price_data['price'] if market_price_data else float('inf')  # Assume infinite cost if no market price data
        return market_price, {}

    total_cost = 0
    crafting_tree = {}

    local_used_reagents = set()  # For item tyupe uniqueness within this recipe level
    for reagent in recipe.recipe_reagents:
        reagent_item_id = get_reagent_item_id(session, reagent, local_used_reagents, server_id)
        if not reagent_item_id:
            return float('inf'), {}

        local_used_reagents.add(reagent_item_id)

        reagent_quantity = reagent.quantity_required

        # Calculate cost for the reagent
        reagent_cost, reagent_tree = calculate_item_cost(session, reagent_item_id, server_id, player_id, depth + 1)
        
        crafting_tree[reagent_item_id] = {
            'cost': reagent_cost,
            'quantity': reagent_quantity,
            'source': 'crafted' if reagent_tree else 'market',
            'children': reagent_tree
        }
        
        # Accumulate the cost
        total_cost += reagent_cost * reagent_quantity

    # Adjust for the quantity produced by the recipe
    unit_cost = total_cost / recipe.quantity_produced if recipe.quantity_produced else total_cost

    # Include any crafting fee (assumed to be 0 for simplicity)
    unit_cost += 0  # Adjust if there's a crafting fee
    
    return unit_cost, crafting_tree



def normalize_values(values):
    """
    Normalize values to a range of 0 to 100 based on their position in the range of all items.
    """
    min_val = min(values)
    max_val = max(values)
    if max_val == min_val:
        return [100 if v == max_val else 0 for v in values]
    else:
        return [(v - min_val) / (max_val - min_val) * 100 for v in values]
    

def calculate_score(profitability_info):
    """
    Calculate score based on normalized profitability factors.
    """
    profits = [info["Profit"] for info in profitability_info.values()]
    profit_margins = [info["Profit Margin"] for info in profitability_info.values()]
    availabilities = [info["Availability"] for info in profitability_info.values()]

    # Normalize values
    normalized_profits = normalize_values(profits)
    normalized_profit_margins = normalize_values(profit_margins)
    normalized_availabilities = normalize_values(availabilities)

    # Calculate scores for each item
    for idx, item_id in enumerate(profitability_info.keys()):
        score = normalized_profits[idx] * normalized_profit_margins[idx] * normalized_availabilities[idx]
        profitability_info[item_id]["Score"] = score

    return profitability_info

def calculate_profitability(session, item_id, server_id, player_id):
    """
    Calculate profitability for an item based on crafting or buying.
    """
    market_price_data = cpo.get_current_price(session, item_id, server_id)
    if not market_price_data:
        return None

    market_price = market_price_data['price']

    # Calculate crafting cost for the item
    crafting_cost, crafting_tree = calculate_item_cost(session, item_id, server_id, player_id)
    profit = market_price - crafting_cost
    profit_margin = (profit / crafting_cost) * 100 if crafting_cost != 0 else 0
    availability = market_price_data['availability'] if market_price_data else 0

    return {
        "Crafting Tree": crafting_tree,
        "Profit": profit,
        "Profit Margin": profit_margin,
        "Crafting Cost": crafting_cost,
        "Market Price": market_price,
        "Availability": availability
    }

def evaluate_all_recipes(session, server_id, player_id, callback=None):
    """
    Evaluate profitability for all recipes in the database.
    """
    all_recipes = session.query(CraftingRecipe).all()
    total_recipes = len(all_recipes)
    profitability_info = {}

    for index, recipe in enumerate(all_recipes):
        
    
        item_id = recipe.result_item_id
        profitability_data = calculate_profitability(session, item_id, server_id, player_id)
        if not profitability_data:
            continue

        profitability_info[item_id] = profitability_data

        # Update the progress bar after processing each recipe
        if callback:
            callback(index + 1, total_recipes)

    # Calculate scores based on normalized values
    profitability_info = calculate_score(profitability_info)

    # Sort items by score and get the top
    top_items = sorted(profitability_info.items(), key=lambda x: x[1]["Score"], reverse=True)[:100]
    return top_items

