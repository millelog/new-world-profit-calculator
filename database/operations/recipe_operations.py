# database/operations/recipe_operations.py

from database.models import CraftingRecipe, RecipeReagent, RecipeSkillRequirement, TradeSkill


def add_recipe(session, recipe_data):
    # Create a new CraftingRecipe object
    recipe = CraftingRecipe(result_item_id=recipe_data["result_item_id"], quantity_produced=recipe_data["quantity_produced"])
    session.add(recipe)
    
    # Commit and flush to ensure recipe has an ID for the relationships
    session.flush()

    # Add the reagents associated with the recipe
    for reagent_data in recipe_data["reagents"]:
        reagent = RecipeReagent(recipe_id=recipe.recipe_id, reagent_item_id=reagent_data["item_id"], quantity_required=reagent_data["quantity_required"])
        session.add(reagent)

    # Add the skill requirements for the recipe
    for skill_req_data in recipe_data["skills_required"]:
        skill = session.query(TradeSkill).filter_by(skill_name=skill_req_data["skill_name"]).first()
        if skill:  # Ensure the skill exists before creating a relationship
            skill_requirement = RecipeSkillRequirement(recipe_id=recipe.recipe_id, skill_id=skill.skill_id, level_required=skill_req_data["level_required"])
            session.add(skill_requirement)

    session.commit()


def get_recipe_by_id(session, recipe_id):
    return session.query(CraftingRecipe).filter_by(recipe_id=recipe_id).first()

def get_recipes_by_item(session, item_id):
    return session.query(CraftingRecipe).filter_by(result_item_id=item_id).all()


