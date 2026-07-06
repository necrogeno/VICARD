import os
import hmac
from flask import Flask, jsonify, request
from flask_cors import CORS

from .extensions import limiter


def create_app():
    app = Flask(__name__)

    # Cap request body size (mitigates payload-flood DoS on /add and /update).
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB

    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    CORS(app, origins=[frontend_url])

    internal_api_key = os.getenv('INTERNAL_API_KEY')
    if not internal_api_key:
        raise RuntimeError(
            'INTERNAL_API_KEY no está configurada. Este backend no debe exponerse sin ella '
            '(protege /gafetdigital/* contra acceso directo no autenticado).'
        )

    @app.before_request
    def require_internal_api_key():
        if not request.path.startswith('/gafetdigital'):
            return None
        supplied = request.headers.get('X-Internal-Api-Key', '')
        if not hmac.compare_digest(supplied, internal_api_key):
            return jsonify({"error": "No autorizado"}), 401

    limiter.init_app(app)

    from .gafetDigital.routes import gafetDigital_bp
    app.register_blueprint(gafetDigital_bp, url_prefix='/gafetdigital')

    return app
