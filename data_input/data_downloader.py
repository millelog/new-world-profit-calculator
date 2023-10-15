# data_input/data_downloader.py

import requests
import json

def download_data(server_id):
    url = f'https://nwmarketprices.com/api/latest-prices/{server_id}/'
    response = requests.get(url)
    response.raise_for_status()  # Check for a valid response
    data = response.json()
    return data

def save_data_to_file(data, filename='download.json'):
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_data_from_file(filename='download.json'):
    with open(filename, 'r') as f:
        return json.load(f)
