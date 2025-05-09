import json
import os

DATA_FILE = 'economy/data.json'

def ensure_user(user_id):
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    if user_id not in data:
        data[user_id] = {'koins': 150}
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)

def get_balance(user_id):
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    return data.get(user_id, {}).get('koins', 0)

def add_koins(user_id, amount):
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    data[user_id]['koins'] += amount
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)
