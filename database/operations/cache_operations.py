from database.models import APICache, engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from database.operations.item_operations import get_item_by_id
import requests
import time
import json


Session = sessionmaker(bind=engine)

def get_cached_data(session, item_id):
    current_time = datetime.now()
    cached_data = session.query(APICache).filter_by(item_id=item_id).first()

    if cached_data:
        # If cached data is from today, return it
        if cached_data.last_cached.date() == current_time.date():
            return json.loads(cached_data.cached_data)
    return None


def update_cache(session, item_id, data):
    serialized_data = json.dumps(data)
    cached_data = session.query(APICache).filter_by(item_id=item_id).first()

    if not cached_data:
        cached_data = APICache(item_id=item_id, cached_data=serialized_data)
        session.add(cached_data)
    else:
        cached_data.cached_data = serialized_data
        cached_data.last_cached = datetime.now()
    
    session.commit()

def fetch_data_from_api(nw_market_id, server_id):
    url = f"https://nwmarketprices.com/0/{server_id}/?cn_id={nw_market_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_price_data(session, item_id, server_id):
    cached_data = get_cached_data(session, item_id)
    if cached_data:
        return cached_data
    
    last_query_time = session.query(APICache).with_entities(APICache.last_cached).order_by(APICache.last_cached.desc()).first()
    if last_query_time and (datetime.now() - last_query_time[0]).total_seconds() < 1:
        time.sleep(1)

    item = get_item_by_id(session, item_id)
    if not item:
        print("Item not found!")
        return None

    nw_market_id = item.nw_market_id
    data_from_api = fetch_data_from_api(nw_market_id, server_id)
    if data_from_api:
        update_cache(session, item_id, data_from_api)
        return data_from_api

    return None
