#database/operations/price_log_operations.py

from sqlalchemy import and_
from database.models import PriceLog

def add_price_log_entry(session, item_id, log_data):
    """
    Adds a new price log entry for an item.
    Args:
        - session: The SQLAlchemy session
        - item_id: ID of the item for which the log entry is being added
        - log_data: Dictionary containing price log details (e.g., price, availability, date, etc.)
    """
    # Check if an entry with the same data already exists
    existing_entry = session.query(PriceLog).filter(
        and_(
            PriceLog.item_id == item_id,
            PriceLog.price == log_data.get('price'),
            PriceLog.availability == log_data.get('availability'),
            PriceLog.last_updated == log_data.get('last_updated'),
            PriceLog.server_id == log_data.get('server_id')
        )
    ).first()

    # If no such entry exists, add a new one
    if existing_entry is None:
        # Create a new PriceLog instance using the provided data
        price_log_entry = PriceLog(item_id=item_id, **log_data)
        
        # Add to the session
        session.add(price_log_entry)
        
        # Commit the session
        session.commit()


def get_price_log_entries(session, item_id, start_date=None, end_date=None):
    """
    Retrieves the price log entries for a specific item, optionally within a specific date range.
    Args:
        - session: The SQLAlchemy session
        - item_id: ID of the item for which the log entries are being fetched
        - start_date: (Optional) Start of the date range for which log entries are to be fetched
        - end_date: (Optional) End of the date range for which log entries are to be fetched
    Returns:
        - List of dictionaries, each containing price log details for the item
    """
    # Query based on the item_id and the optional date range
    query = session.query(PriceLog).filter(PriceLog.item_id == item_id)
    
    if start_date and end_date:
        query = query.filter(and_(PriceLog.last_updated >= start_date, PriceLog.last_updated <= end_date))
    elif start_date:
        query = query.filter(PriceLog.last_updated >= start_date)
    elif end_date:
        query = query.filter(PriceLog.last_updated <= end_date)
    
    # Convert the result to a list of dictionaries
    return [entry.__dict__ for entry in query.all()]
