#database/operations/current_price_operations.py

from database.models import CurrentPrice

def add_current_price(session, item_id, price_data):
    """
    Adds a new current price entry for an item.
    Args:
        - session: The SQLAlchemy session
        - item_id: ID of the item for which the current price is being added
        - price_data: Dictionary containing current price details (e.g., price, availability, etc.)
    """
    # Create a new CurrentPrice instance using the provided data
    current_price = CurrentPrice(item_id=item_id, **price_data)
    
    # Add to the session
    session.add(current_price)
    
    # Commit the session
    session.commit()

def update_current_price(session, item_id, new_price_data):
    """
    Updates the current price details for a specific item.
    Args:
        - session: The SQLAlchemy session
        - item_id: ID of the item for which the current price is being updated
        - new_price_data: Dictionary containing updated price details
    """
    # Query for the existing entry
    current_price = session.query(CurrentPrice).filter(CurrentPrice.item_id == item_id).first()
    
    # Update the values
    for key, value in new_price_data.items():
        setattr(current_price, key, value)
    
    # Commit the session
    session.commit()

def get_current_price(session, item_id):
    """
    Retrieves the current price details for a specific item.
    Args:
        - session: The SQLAlchemy session
        - item_id: ID of the item for which the current price details are being fetched
    Returns:
        - Dictionary containing current price details for the item
    """
    # Query for the current price entry for the specified item
    current_price = session.query(CurrentPrice).filter(CurrentPrice.item_id == item_id).first()
    
    # Convert the result to a dictionary (excluding SQLAlchemy's internal attributes)
    if current_price:
        return {key: value for key, value in current_price.__dict__.items() if not key.startswith('_')}
    return None

