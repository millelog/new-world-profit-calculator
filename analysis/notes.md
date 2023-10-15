# Crafting Profitability Calculations (`crafting_profit.py`)

## `calculate_crafting_cost(session, recipe_id) -> float`
- **Input**:
  - `session`: SQLAlchemy session object for database interaction.
  - `recipe_id`: ID of the crafting recipe.
- **Output**:
  - Returns the total cost of crafting for the specified recipe.
- **Pseudocode**:
  1. Fetch the recipe from the database using the `recipe_id`.
  2. Iterate over each reagent in the recipe's reagents.
  3. For each reagent, get the current price from the `CurrentPrice` table.
  4. Sum up the cost of all reagents and return.

## `calculate_crafting_profit(session, recipe_id) -> float`
- **Input**:
  - `session`: SQLAlchemy session object for database interaction.
  - `recipe_id`: ID of the crafting recipe.
- **Output**:
  - Returns the profit from crafting for the specified recipe.
- **Pseudocode**:
  1. Calculate the crafting cost using `calculate_crafting_cost`.
  2. Get the selling price of the resulting item from the `CurrentPrice` table.
  3. Subtract the crafting cost from the selling price to get the profit and return.

---

# Historical Price Tracking and Analysis (`historical_price_analysis.py`)

## `get_price_trend(session, item_id, start_date, end_date) -> dict`
- **Input**:
  - `session`: SQLAlchemy session object for database interaction.
  - `item_id`: ID of the item.
  - `start_date`, `end_date`: Date range for analysis.
- **Output**:
  - Returns a dictionary with date as key and price as value.
- **Pseudocode**:
  1. Fetch all price log entries for the specified item and date range from the `PriceLog` table.
  2. Create a dictionary with date as key and price as value.
  3. Return the dictionary.

---

# Recommendations Module (`recommendations.py`)

## `get_profitable_crafting_recipes(session) -> list`
- **Input**:
  - `session`: SQLAlchemy session object for database interaction.
- **Output**:
  - Returns a list of profitable crafting recipes.
- **Pseudocode**:
  1. Fetch all crafting recipes from the `CraftingRecipe` table.
  2. For each recipe, calculate the profit using `calculate_crafting_profit` from `crafting_profit.py`.
  3. If the profit is positive, add the recipe to the list of profitable recipes.
  4. Return the list of profitable recipes.

## `make_buy_sell_recommendations(session, player_id) -> dict`
- **Input**:
  - `session`: SQLAlchemy session object for database interaction.
  - `player_id`: ID of the player.
- **Output**:
  - Returns a dictionary with buy and sell recommendations.
- **Pseudocode**:
  1. Get profitable crafting recipes using `get_profitable_crafting_recipes`.
  2. For each profitable recipe, check the availability and price of reagents in the `CurrentPrice` table.
  3. Make buy recommendations for reagents that are cheap and sell recommendations for crafted items that are profitable.
  4. Update the `Transaction` table with the new transactions (buy/sell).
  5. Return the recommendations dictionary.

