# database/mongo.py
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()

# Conexión a MongoDB
client = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi('1'))
db = client.silverkoi

users_collection = db.users
cards_collection = db.cards

def ensure_user(user_id):
    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({
            "user_id": user_id,
            "koins": 150,
            "frames": [],
            "cards": [],
            "inventory": {}
        })

def get_user_balance(user_id):
    ensure_user(user_id)
    user = users_collection.find_one({"user_id": user_id})
    return user.get("koins", 0)

def add_user_koins(user_id, amount):
    ensure_user(user_id)
    users_collection.update_one(
        {"user_id": user_id},
        {"$inc": {"koins": amount}}
    )

def remove_user_koins(user_id, amount):
    ensure_user(user_id)
    users_collection.update_one(
        {"user_id": user_id},
        {"$inc": {"koins": -amount}}
    )

def get_user_frames(user_id):
    ensure_user(user_id)
    user = users_collection.find_one({"user_id": user_id})
    return user.get("frames", [])

def add_user_frame(user_id, frame_type):
    ensure_user(user_id)
    users_collection.update_one(
        {"user_id": user_id},
        {"$addToSet": {"frames": frame_type}}
    )

def add_card_to_user(user_id, card_data):
    ensure_user(user_id)
    
    # Guardar carta en la colección general si no existe
    if not cards_collection.find_one({"card_id": card_data["name"]}):
        cards_collection.insert_one({
            "card_id": card_data["name"],
            "series": card_data["series"],
            "image_url": card_data["image"],
            "rarity": card_data.get("rarity", "R")
        })
    
    # Añadir a la colección del usuario
    users_collection.update_one(
        {"user_id": user_id},
        {"$addToSet": {"cards": card_data["name"]}}
    )