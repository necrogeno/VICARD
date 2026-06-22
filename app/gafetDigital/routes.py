from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
from ..database import coleccion # Importamos la colección desde database.py
from .services import consulta_empleado, agregar_registro, limpiar_acentos, actualizar_datos, borrar_registro, consulta_All
import unicodedata
# Creamos el Blueprint
gafetDigital_bp = Blueprint('gafetDigital', __name__)

# --- Rutas del Blueprint ---
@gafetDigital_bp.route('/findusuario', methods=['GET'])
def obtenerUsuario():

    return jsonify("poner el json aqui pendejo"),200




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
    datos_recibidos = request.get_json()
    if not datos_recibidos:
        return jsonify({"error": "No se enviaron datos"}), 400
    
    # Suponiendo que agregar_registro está definida arriba
    try:
        datos_limpios = limpiar_acentos(datos_recibidos)
        resultado = coleccion.insert_one(datos_limpios)
        return jsonify({"id_insertado": str(resultado.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@gafetDigital_bp.route('/update/<string:id>', methods=['PUT'])
def actualizar(id):
    # 1. Obtenemos los nuevos datos desde el JSON del body
    datos_recibidos = request.get_json()
    
    if not datos_recibidos:
        return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400

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