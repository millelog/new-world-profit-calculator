import os
import requests
import json

def delete_old_data_file(filename='download.json'):
    if os.path.exists(filename):
        os.remove(filename)

def download_data(server_id):
    url = f'https://nwmarketprices.com/api/latest-prices/{server_id}/'
    response = requests.get(url)
    response.raise_for_status()  # Check for a valid response
    data = response.json()
    return data

def save_data_to_file(data, filename='download.json'):
    delete_old_data_file(filename)  
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_data_from_file(filename='download.json'):
    with open(filename, 'r') as f:
        return json.load(f)
