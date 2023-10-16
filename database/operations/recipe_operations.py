# database/operations/recipe_operations.py

from database.models import CraftingRecipe, ItemType, RecipeReagent, RecipeSkillRequirement, TradeSkill


def add_recipe(session, recipe_data):
    # Create a new CraftingRecipe object
    recipe = CraftingRecipe(result_item_id=recipe_data["result_item_id"], quantity_produced=recipe_data["quantity_produced"])
    session.add(recipe)
    
    # Commit and flush to ensure recipe has an ID for the relationships
    session.flush()

    # Add the reagents associated with the recipe
    for reagent_data in recipe_data["reagents"]:
        # Check if reagent_data has an item_id key
        if "item_id" in reagent_data:
            reagent = RecipeReagent(
                recipe_id=recipe.recipe_id, 
                reagent_item_id=reagent_data["item_id"], 
                quantity_required=reagent_data["quantity_required"]
            )
            session.add(reagent)
        
        # Check if reagent_data has an item_type key
        elif "item_type" in reagent_data:
            # Query the ItemType to get its item_type_id
            item_type = session.query(ItemType).filter_by(item_type_name=reagent_data["item_type"]).first()
            
            if item_type:  # Ensure the item_type exists before inserting
                reagent = RecipeReagent(
                    recipe_id=recipe.recipe_id, 
                    reagent_item_type_id=item_type.item_type_id, 
                    quantity_required=reagent_data["quantity_required"]
                )
                session.add(reagent)

    session.commit()


def get_recipe_by_id(session, recipe_id):
    return session.query(CraftingRecipe).filter_by(recipe_id=recipe_id).first()

def get_recipes_by_item(session, item_id):
    return session.query(CraftingRecipe).filter_by(result_item_id=item_id).all()


