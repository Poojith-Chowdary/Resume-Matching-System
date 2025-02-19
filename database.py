from flask_pymongo import PyMongo
from flask import Flask
from config import Config

mongo = PyMongo()

def init_db(app):
    app.config["MONGO_URI"] = Config.MONGO_URI
    
    mongo.init_app(app)

def get_db():
    return mongo.db  # Correct way to access the database
