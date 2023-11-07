#analysis/buy_profit.py
import database.operations.current_price_operations as cpo
from analysis.price_analysis import analyze_market_health

class BuyProfitAnalyzer:
    def __init__(self, session, server_id, player_id):
        self.session = session
        self.server_id = server_id
        self.player_id = player_id

    def evaluate_all_buy_prices(self):
        """
        Evaluate all buy prices in the database to find profitable buying opportunities.
        """
        # Get items with profitable buy prices
        profitable_items_list = cpo.get_profitable_buy_items(self.session, self.server_id)

        # Dictionary to store profitability information
        profitability_info = {}

        # Ensure profitable_items_list is actually a list of dictionaries
        if not all(isinstance(item, dict) for item in profitable_items_list):
            raise ValueError("Expected a list of dictionaries")

        for item_data in profitable_items_list:
            item_id = item_data.get('item_id')
            if item_id is None:
                continue  # Skip if no item_id is present

            current_price = cpo.get_current_price(self.session, item_id, self.server_id)

            # Ensure the data has buy price and market price information
            if 'highest_buy_order' not in current_price or 'price' not in current_price:
                continue

            # Update item_data with current price data and average availability
            item_data.update({
                "Market Price": current_price['price'],
                "Buy Price": current_price['highest_buy_order'],
                "Profit Margin": ((current_price['price']-current_price['highest_buy_order'])/current_price['highest_buy_order'])*100,
            })

            profitability_info[item_id] = item_data

        # Analyze market health and rank items based on profit potential
        ranked_profitable_items = analyze_market_health(self.session, self.server_id, profitability_info, "buy")

        return ranked_profitable_items

