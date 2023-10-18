#database/operations/item_operations.py

from database.models import Item, item_itemtype_association
import database.operations.current_price_operations as cpo



def add_item(session, item_data):
    new_item = Item(**item_data)
    session.add(new_item)
    session.commit()
    return new_item.item_id


def update_item(session, item_id, new_data):
    item = session.query(Item).filter_by(item_id=item_id).first()
    if item:
        for key, value in new_data.items():
            setattr(item, key, value)
        session.commit()
        return True 
    return False


def get_item_by_id(session, item_id):
    item = session.query(Item).filter_by(item_id=item_id).first()
    return item 

def get_item_by_name(session, item_name):
    item = session.query(Item).filter_by(name=item_name).first()
    return item

def get_items_for_item_type(session, item_type_id, server_id):
    """
    Retrieves all items associated with a given item type, ordered by their market cost.
    """
    items = session.query(Item).join(item_itemtype_association).filter(
        item_itemtype_association.c.item_type_id == item_type_id
    ).all()
    # Fetch market prices and order by them. 
    # Note: You'd need a function to get the price for each item.
    items_sorted = sorted(items, key=lambda item: cpo.get_current_price(session, item.item_id, server_id)['price'] if cpo.get_current_price(session, item.item_id, server_id) else float('inf'))
    return items_sorted
