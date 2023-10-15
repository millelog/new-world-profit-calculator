#data_input/json_parse.py

from datetime import datetime
from database.operations import current_price_operations, price_log_operations

def process_json_data(session, json_data, server_id):
    """
    Processes the given JSON data and updates both PriceLog and CurrentPrice tables.
    
    Args:
    - session: The SQLAlchemy session
    - json_data: List of dictionaries containing item price data
    - server_id: ID of the server for which the data is being processed
    """
    
    for item_data in json_data:
        # Extract necessary details
        item_id = item_data["ItemId"]
        # Convert the string representation of the datetime to a datetime object
        last_updated = datetime.strptime(item_data["LastUpdated"], "%Y-%m-%dT%H:%M:%S.%f")
        
        log_data = {
            "price": float(item_data["Price"]),
            "availability": item_data["Availability"],
            "last_updated": last_updated,
            "highest_buy_order": item_data["HighestBuyOrder"] if item_data["HighestBuyOrder"] else None,
            "qty": item_data["Qty"] if item_data["Qty"] else None,
            "server_id": server_id  
        }
        
        # Add entry to PriceLog
        price_log_operations.add_price_log_entry(session, item_id, log_data)
        
        # Check if item exists in CurrentPrice
        current_price_entry = current_price_operations.get_current_price(session, item_id)
        if current_price_entry:
            # Update the existing entry
            current_price_operations.update_current_price(session, item_id, log_data)
        else:
            # Add new entry
            current_price_operations.add_current_price(session, item_id, log_data)
