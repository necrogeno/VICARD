from bson.objectid import ObjectId
from ..database import coleccion
import unicodedata


def limpiar_acentos(datos):

    if isinstance(datos, dict):
        # Aplicamos la limpieza a cada valor del diccionario
        return {k: limpiar_acentos(v) for k, v in datos.items()}
    elif isinstance(datos, list):
        # Si es una lista, limpiamos cada elemento
        return [limpiar_acentos(i) for i in datos]
    elif isinstance(datos, str):
        # Lógica principal para quitar acentos
        # NFKD separa el carácter del acento, 'Mn' filtra los acentos
        return "".join(
            c for c in unicodedata.normalize('NFKD', datos)
            if unicodedata.category(c) != 'Mn'
        )
    else:
        # Si es un número o booleano, se devuelve tal cual
        return datos


def consulta_empleado(id_string):
    try:
        datos = coleccion.find_one({"_id": ObjectId(id_string)})
        if datos:
            datos["_id"] = str(datos["_id"])
            return datos
        return None
    except Exception:
        return {"error": "Formato de ID inválido"}


def agregar_registro(datos):
    try:
        # Insertamos el diccionario directamente en MongoDB
        resultado = coleccion.insert_one(datos)
        
        # Retornamos el ID generado por Mongo convertido a string
        return {
            "mensaje": "Registro agregado correctamente",
            "id_insertado": str(resultado.inserted_id),
            "status": "success"
        }
    except Exception as e:
        print(f"Error al agregar registro: {e}")
        return {"error": "Error interno al agregar registro"}


def actualizar_datos(id_string, datos_nuevos):
    try:
        # 1. Intentamos actualizar el documento usando el _id
        # El operador $set reemplaza solo los campos incluidos en datos_nuevos
        resultado = coleccion.update_one(
            {"_id": ObjectId(id_string)}, 
            {"$set": datos_nuevos}
        )
        
        if resultado.matched_count == 0:
            return None # No se encontró el registro
            
        return {
            "mensaje": "Registro actualizado correctamente",
            "modificado": resultado.modified_count > 0,
            "status": "success"
        }
    except Exception as e:
        print(f"Error al actualizar: {e}")
        return {"error": "ID inválido o error interno"}


def borrar_registro(id_string):
    try:
        # Intentamos eliminar el documento que coincida con el ObjectId
        resultado = coleccion.delete_one({"_id": ObjectId(id_string)})
        
        # deleted_count nos dice cuántos documentos se borraron (0 o 1)
        if resultado.deleted_count == 0:
            return None # No se encontró nada para borrar
            
        return {
            "mensaje": "Registro eliminado correctamente",
            "status": "success"
        }
    except Exception as e:
        print(f"Error al borrar: {e}")
        return {"error": "ID inválido o error interno del servidor"}