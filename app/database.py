import os
from pymongo import MongoClient

URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
client = MongoClient(URI)
db = client.get_database("GafetDigital")
coleccion = db.get_collection("GafetDigital")
coleccionUsuarios = db.get_collection("UsuarioGafet")