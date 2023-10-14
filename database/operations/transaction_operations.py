# database/operations/transaction_operations.py

from database.models import Transaction


def add_transaction(session, transaction_data):
    # Create a new Transaction object
    transaction = Transaction(
        item_id=transaction_data["item_id"],
        player_id=transaction_data["player_id"],
        transaction_type=transaction_data["transaction_type"],
        quantity=transaction_data["quantity"],
        total_price=transaction_data["total_price"],
        transaction_date=transaction_data["transaction_date"],
        server_id=transaction_data["server_id"]
    )
    session.add(transaction)
    session.commit()


def get_transaction_by_id(session, transaction_id):
    return session.query(Transaction).filter_by(transaction_id=transaction_id).first()

def get_transactions_by_player(session, player_id):
    return session.query(Transaction).filter_by(player_id=player_id).all()

def get_transactions_by_item(session, item_id):
    return session.query(Transaction).filter_by(item_id=item_id).all()
