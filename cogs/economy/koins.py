import json
import os

DATA_FILE = "data/users.json"

# Crea carpeta data si no existe
os.makedirs("data", exist_ok=True)

# Inicializa archivo si no existe
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def ensure_user(user_id):
    data = load_data()
    if user_id not in data:
        data[user_id] = {"koins": 150}
        save_data(data)

def get_balance(user_id):
    data = load_data()
    return data.get(user_id, {}).get("koins", 0)

def add_koins(user_id, amount):
    data = load_data()
    if user_id in data:
        data[user_id]["koins"] += amount
        save_data(data)
