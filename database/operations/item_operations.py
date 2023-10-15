#database/operations/item_operations.py

from database.models import Item 


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