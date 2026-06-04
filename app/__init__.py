from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    # Importamos el blueprint
    from .gafetDigital.routes import gafetDigital_bp
    
    # Lo registramos con un prefijo. 
    # Ahora todas tus rutas empezarán con /api (ej: /api/encontrar/123)
    app.register_blueprint(gafetDigital_bp, url_prefix='/gafetdigital')

    return app