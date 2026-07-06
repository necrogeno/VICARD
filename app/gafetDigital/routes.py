from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
from ..database import coleccion # Importamos la colección desde database.py
from ..extensions import limiter
from .services import consulta_empleado, consulta_usuario, consulta_usuario_por_rfc, agregar_registro, limpiar_acentos, actualizar_datos, borrar_registro, consulta_All
import unicodedata
# Creamos el Blueprint
gafetDigital_bp = Blueprint('gafetDigital', __name__)


def payload_tiene_claves_inseguras(datos):
    """Rechaza claves de nivel superior tipo operador de Mongo ($set, $where, ...)
    para que un payload de /add o /update no pueda inyectar operadores dentro del
    documento que se pasa a insert_one/$set."""
    if not isinstance(datos, dict):
        return True
    return any(isinstance(k, str) and (k.startswith('$') or '.' in k) for k in datos.keys())


# --- Rutas del Blueprint ---
@gafetDigital_bp.route('/findusuario/<string:correo>', methods=['GET'])
@limiter.limit("10 per minute")
def obtenerUsuario(correo):
    # Llamamos a la función de la imagen pasándole el correo de la URL
    resultado = consulta_usuario(correo)
    
    # Si no se encontró el usuario (retornó None)
    if resultado is None:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404
        
    # Si la función atrapó una excepción y regresó el diccionario de error
    if isinstance(resultado, dict) and "error" in resultado:
        return jsonify(resultado), 400
        
    # Si todo salió bien, regresamos los datos con estatus 200 OK
    return jsonify(resultado), 200


@gafetDigital_bp.route('/findusuariorfc/<string:rfc>', methods=['GET'])
@limiter.limit("10 per minute")
def obtenerUsuarioPorRfc(rfc):
    resultado = consulta_usuario_por_rfc(rfc)
    if resultado is None:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404
    if isinstance(resultado, dict) and "error" in resultado:
        return jsonify(resultado), 400
    return jsonify(resultado), 200


@gafetDigital_bp.route('/find', methods=['GET'])
def obtenerAll():
    resultado = consulta_All()
    
    # Validamos si la función de servicio devolvió un diccionario de error
    if isinstance(resultado, dict) and "error" in resultado:
        return jsonify(resultado), 500
        
    # Si todo está bien, mandamos la lista de usuarios con un estatus 200 OK
    return jsonify(resultado), 200



@gafetDigital_bp.route('/find/<string:id>', methods=['GET'])
def obtener_tareas(id):
    resultado = consulta_empleado(id)
    if resultado is None:
        return jsonify({"mensaje": "Empleado no encontrado"}), 404
    if "error" in resultado:
        return jsonify(resultado), 400
    return jsonify(resultado), 200

@gafetDigital_bp.route('/add', methods=['POST'])
def agregar():
    datos_recibidos = request.get_json(silent=True)
    if not datos_recibidos:
        return jsonify({"error": "No se enviaron datos"}), 400
    if payload_tiene_claves_inseguras(datos_recibidos):
        return jsonify({"error": "Payload inválido"}), 400

    try:
        datos_limpios = limpiar_acentos(datos_recibidos)
        resultado = coleccion.insert_one(datos_limpios)
        return jsonify({"id_insertado": str(resultado.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@gafetDigital_bp.route('/update/<string:id>', methods=['PUT'])
def actualizar(id):
    # 1. Obtenemos los nuevos datos desde el JSON del body
    datos_recibidos = request.get_json(silent=True)

    if not datos_recibidos:
        return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400
    if payload_tiene_claves_inseguras(datos_recibidos):
        return jsonify({"error": "Payload inválido"}), 400

    # 2. Llamamos a la lógica pasándole el ID de la URL y los datos del Body
    datos_limpios = limpiar_acentos(datos_recibidos)
    resultado = actualizar_datos(id, datos_limpios)
    
    # 3. Manejo de respuestas
    if resultado is None:
        return jsonify({"mensaje": "No se encontró el registro para actualizar"}), 404
        
    if "error" in resultado:
        return jsonify(resultado), 400
        
    return jsonify(resultado), 200

@gafetDigital_bp.route('/delete/<string:id>', methods=['DELETE'])
def borrar(id):
    # Llamamos a la función lógica
    resultado = borrar_registro(id)
    
    # Si no se encontró el registro
    if resultado is None:
        return jsonify({"mensaje": "No se encontró el registro para eliminar"}), 404
    
    # Si hubo un error de formato de ID
    if "error" in resultado:
        return jsonify(resultado), 400
        
    return jsonify(resultado), 200
# Añade aquí el resto de tus rutas (actualizar, borrar) usando @api_bp.route