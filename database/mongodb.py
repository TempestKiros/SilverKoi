from pymongo import MongoClient
import os

# Conexión a MongoDB Atlas (reemplaza el URI con el de tu propia base de datos)
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')  # Si tienes MongoDB local
client = MongoClient(MONGO_URI)

# Selecciona la base de datos y la colección que usarás
db = client['SilverKoiDB']
users_collection = db['users']

def get_user_data(user_id):
    return users_collection.find_one({"user_id": user_id})

def create_user(user_id):
    if get_user_data(user_id) is None:
        users_collection.insert_one({"user_id": user_id, "koins": 150, "cards": []})

def update_koins(user_id, amount):
    users_collection.update_one({"user_id": user_id}, {"$inc": {"koins": amount}})
