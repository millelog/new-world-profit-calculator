#analysis/buy_profit.py

import numpy as np
from database.operations.cache_operations import get_price_data


sql = """
SELECT i.item_name,
       availability * (price - highest_buy_order) as potential_profit,
       ROUND(((price - highest_buy_order) / highest_buy_order) * 100, 2) as profit_margin_percentage,
       p.*
FROM current_prices p
INNER JOIN items i ON p.item_id = i.item_id
LEFT OUTER JOIN crafting_recipes r ON r.result_item_id = p.item_id
WHERE availability > 1
AND qty > 1
AND highest_buy_order > 0.1
AND highest_buy_order IS NOT NULL
AND price > highest_buy_order * 1.20
AND r.result_item_id IS NULL
ORDER BY ROUND(availability * ((price - highest_buy_order) / highest_buy_order), 2) DESC, availability DESC
"""