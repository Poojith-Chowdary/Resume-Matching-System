import os

class Config:
    SECRET_KEY = "oolaalalalallloolala"
    
    # MongoDB
    MONGO_URI = "mongodb+srv://Mahideep:WSEm1SbQYyCvdYqd@irms-cluster.fsoky.mongodb.net/hr_details?retryWrites=true&w=majority&appName=IRMS-Cluster"

    # JWT
    JWT_SECRET_KEY = "b0778be64d1515eaf7094b15502dbad26c4967a2607c5b4c53f441a0faa2f06c0f5d5440949dd5bc4fe56bff133e6b1ca2d38d8e01b658e9ffdd8bcd5b45a132"

    # OAuth Credentials
    GOOGLE_CLIENT_ID = "F5pZWXWhCVc1WiFKBhPQl4qvLHF4OPrn"
    GOOGLE_CLIENT_SECRET = "oojiQ58A-pIB5N7k-pJ_plNQMl1g3eONZ8mt_XXmJTKEqKAfUUOWcVbl0FV7qLmk"

    # Email Settings
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = "jhondoe7001@gmail.com"
    MAIL_PASSWORD = "wvqtgejhkezaezuq"
