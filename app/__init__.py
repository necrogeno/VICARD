from flask import Flask

def create_app():
    app = Flask(__name__)

    # Importamos el blueprint
    from .gafetDigital.routes import gafetDigital_bp
    
    # Lo registramos con un prefijo. 
    # Ahora todas tus rutas empezarán con /api (ej: /api/encontrar/123)
    app.register_blueprint(gafetDigital_bp, url_prefix='/gafetdigital')

    return app