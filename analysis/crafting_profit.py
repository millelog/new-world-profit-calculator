#analysis/crafting_profit.py

from database.models import CraftingRecipe
import database.operations.current_price_operations as cpo
import database.operations.recipe_operations as ro
import database.operations.player_operations as po
import database.operations.item_operations as io

class CraftingProfitAnalyzer:
    def __init__(self, session, server_id, player_id):
        self.session = session
        self.server_id = server_id
        self.player_id = player_id


    def calculate_item_cost(self, item_id, market_price):
        """
        Calculates the cost of an item either by crafting or market price.
        Compares crafting cost with market price and stops crafting computation 
        if the cost exceeds market price.
        """
        # Fetch potential crafting recipes for the item
        recipes = ro.get_recipes_by_item(self.session, item_id)

        # If no crafting recipes are found, return the market price
        if not recipes:
            return market_price, {}

        # For each crafting recipe, determine the cost and compare it to the market price
        cheapest_crafting_cost = float('inf')
        cheapest_crafting_tree = {}
        for recipe in recipes:
            crafting_cost, crafting_tree = self.get_crafting_cost(recipe, market_price)

            # If the crafting cost for this recipe is cheaper, update the cheapest cost and tree
            if crafting_cost < cheapest_crafting_cost:
                cheapest_crafting_cost = crafting_cost
                cheapest_crafting_tree = crafting_tree

            # If at any point the crafting cost surpasses the market price, return market price
            if cheapest_crafting_cost > market_price:
                return market_price, {}
            

        return cheapest_crafting_cost, cheapest_crafting_tree


    def get_reagent_item_id(self, reagent, used_reagents):
        """
        Determines the reagent item ID for crafting, prioritizing specific item IDs or selecting from available item types.
        """
        if reagent.reagent_item_id:
            return reagent.reagent_item_id

        potential_items = io.get_items_for_item_type(self.session, reagent.reagent_item_type_id, self.server_id)  # Returns sorted by market price
        potential_items = [item for item in potential_items if item.item_id not in used_reagents]  # Filter out already used reagents

        if not potential_items:
            return None  # No valid items to use for this reagent

        # Assuming potential_items is sorted by price, return the cheapest one
        return potential_items[0].item_id


    def get_crafting_cost(self, recipe, market_price, accumulated_cost=0):
        """
        Calculates the crafting cost of a given recipe while considering the market price.
        """
        # Check if the player can craft the given recipe
        can_craft = po.can_craft_recipe(self.session, self.player_id, recipe.recipe_id)
        if not can_craft:
            result_market_price_data = cpo.get_current_price(self.session, recipe.result_item_id, self.server_id)
            return result_market_price_data['price'] if result_market_price_data else float('inf'), {}

        total_cost = accumulated_cost
        crafting_tree = {}

        local_used_reagents = set()  # For item type uniqueness within this recipe level
        for reagent in recipe.recipe_reagents:
            reagent_item_id = self.get_reagent_item_id(reagent, local_used_reagents)
            if not reagent_item_id:
                return float('inf'), {}

            local_used_reagents.add(reagent_item_id)

            reagent_quantity = reagent.quantity_required

            # Calculate cost for the reagent
            reagent_market_price_data = cpo.get_current_price(self.session, reagent_item_id, self.server_id)
            reagent_market_price = reagent_market_price_data['price'] if reagent_market_price_data else float('inf')
            reagent_cost, reagent_tree = self.calculate_item_cost(reagent_item_id, reagent_market_price)


            # If at any point, the accumulated cost surpasses the market price, return market price
            total_cost += reagent_cost * reagent_quantity
            if total_cost > market_price:
                return market_price, {}

            crafting_tree[reagent_item_id] = {
                'cost': reagent_cost,
                'quantity': reagent_quantity,
                'source': 'crafted' if reagent_tree else 'market',
                'children': reagent_tree
            }

        # Adjust for the quantity produced by the recipe
        unit_cost = total_cost / recipe.quantity_produced if recipe.quantity_produced else total_cost

        # Include any crafting fee (assumed to be 0 for simplicity)
        unit_cost += 0  # Adjust if there's a crafting fee
        
        return unit_cost, crafting_tree


    def _normalize_values(self, values):
        """
        Normalize values to a range of 0 to 100 based on their position in the range of all items.
        """
        min_val = min(values)
        max_val = max(values)
        if max_val == min_val:
            return [100 if v == max_val else 0 for v in values]
        else:
            return [(v - min_val) / (max_val - min_val) * 100 for v in values]
        

    def calculate_score(self, profitability_info):
        """
        Calculate score based on normalized profitability factors.
        """
        profits = [info["Profit"] for info in profitability_info.values()]
        profit_margins = [info["Profit Margin"] for info in profitability_info.values()]
        availabilities = [info["Availability"] for info in profitability_info.values()]

        # Normalize values
        normalized_profits = self._normalize_values(profits)
        normalized_profit_margins = self._normalize_values(profit_margins)
        normalized_availabilities = self._normalize_values(availabilities)

        # Calculate scores for each item
        for idx, item_id in enumerate(profitability_info.keys()):
            score = normalized_profit_margins[idx] #* normalized_profits[idx] * normalized_availabilities[idx]
            profitability_info[item_id]["Score"] = score

        return profitability_info


    def calculate_profitability(self, item_id):
        """
        Calculate profitability for an item based on crafting or buying.
        """
        market_price_data = cpo.get_current_price(self.session, item_id, self.server_id)
        if not market_price_data:
            return None

        market_price = market_price_data['price']

        # Calculate crafting cost for the item
        crafting_cost, crafting_tree = self.calculate_item_cost(item_id, market_price)  # Pass the market_price here
        profit = market_price - crafting_cost
        profit_margin = (profit / crafting_cost) * 100 if crafting_cost != 0 else 0
        availability = market_price_data['availability'] if market_price_data else 0

        return {
            "Item ID": item_id,
            "Crafting Tree": crafting_tree,
            "Profit": profit,
            "Profit Margin": profit_margin,
            "Crafting Cost": crafting_cost,
            "Market Price": market_price,
            "Availability": availability
        }



    def evaluate_all_recipes(self, callback=None):
        """
        Evaluate profitability for all recipes in the database.
        """
        all_recipes = self.session.query(CraftingRecipe).all()
        total_recipes = len(all_recipes)
        profitability_info = {}

        for index, recipe in enumerate(all_recipes):
            item_id = recipe.result_item_id
            market_price_data = cpo.get_current_price(self.session, item_id, self.server_id)
            if not market_price_data:
                continue

            market_price = market_price_data['price']
            
            profitability_data = self.calculate_profitability(item_id)
            
            if not profitability_data:
                continue

            profitability_info[item_id] = profitability_data

            # Update the progress bar after processing each recipe
            if callback:
                callback(index + 1, total_recipes)

        # Calculate scores based on normalized values
        profitability_info = self.calculate_score(profitability_info)

        # Sort items by score and get the top
        top_items = sorted(
            [item for item in profitability_info.items() if item[1]["Profit"] > 0],
            key=lambda x: x[1]["Score"], 
            reverse=True
        )[:100]

        return top_items

