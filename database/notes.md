Item:
- item_id (PK)
- item_name
- current_price -> CurrentPrice (1:1)
- price_logs -> PriceLog (1:N)
- crafting_recipes -> CraftingRecipe (1:N)
- recipe_reagents -> RecipeReagent (1:N)
- item_types -> ItemType (N:N)

ItemType:
- item_type_id (PK)
- item_type_name
- items -> Item (N:N)

item_itemtype_association:
- item_id (FK -> Item)
- item_type_id (FK -> ItemType)

PriceLog:
- log_id (PK)
- item_id (FK -> Item)
- price, availability, last_updated, highest_buy_order, qty
- server_id (FK -> Server)

CurrentPrice:
- item_id (PK, FK -> Item)
- price, availability, last_updated, highest_buy_order, qty
- server_id (FK -> Server)

TradeSkill:
- skill_id (PK)
- skill_name
- players -> PlayerSkill (1:N)

RecipeSkillRequirement:
- recipe_id (PK, FK -> CraftingRecipe)
- skill_id (PK, FK -> TradeSkill)
- level_required

CraftingRecipe:
- recipe_id (PK)
- result_item_id (FK -> Item)
- quantity_produced
- recipe_reagents -> RecipeReagent (1:N)
- skill_requirements -> RecipeSkillRequirement (1:N)

RecipeReagent:
- id (PK)
- recipe_id (FK -> CraftingRecipe)
- reagent_item_id (FK -> Item, nullable=True)
- reagent_item_type_id (FK -> ItemType, nullable=True) 
- quantity_required


Player:
- player_id (PK)
- player_name
- server_id (FK -> Server)
- skills -> PlayerSkill (1:N)
- transactions -> Transaction (1:N)

PlayerSkill:
- player_id (PK, FK -> Player)
- skill_id (PK, FK -> TradeSkill)
- skill_level

Transaction:
- transaction_id (PK)
- item_id (FK -> Item)
- player_id (FK -> Player)
- transaction_type, quantity, total_price, transaction_date
- server_id (FK -> Server)

Server:
- server_id (PK)
- server_name
- price_logs -> PriceLog (1:N)
- current_prices -> CurrentPrice (1:N)
- players -> Player (1:N)
- transactions -> Transaction (1:N)
