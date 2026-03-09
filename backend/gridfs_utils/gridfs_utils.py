from gridfs import GridFS
from bson import ObjectId
from crud.common import db

fs = GridFS(db)


def subir_archivo(ruta_archivo, nombre_archivo=None, metadata=None):
    """
    Sube un archivo a GridFS.

    Parámetros:
    - ruta_archivo: ruta local del archivo
    - nombre_archivo: nombre opcional para guardar en GridFS
    - metadata: diccionario opcional con metadatos
    """

    with open(ruta_archivo, "rb") as archivo:
        contenido = archivo.read()

    if nombre_archivo is None:
        nombre_archivo = ruta_archivo.split("\\")[-1].split("/")[-1]

    file_id = fs.put(
        contenido,
        filename=nombre_archivo,
        metadata=metadata or {}
    )

    return {
        "ok": True,
        "file_id": file_id,
        "filename": nombre_archivo
    }


def listar_archivos():
    """
    Lista todos los archivos almacenados en GridFS.
    """

    archivos = []
    for archivo in fs.find():
        archivos.append({
            "file_id": archivo._id,
            "filename": archivo.filename,
            "length": archivo.length,
            "upload_date": archivo.upload_date,
            "metadata": getattr(archivo, "metadata", {})
        })

    return archivos


def descargar_archivo(file_id, ruta_salida):
    """
    Descarga un archivo desde GridFS.

    Parámetros:
    - file_id: ObjectId o string del archivo
    - ruta_salida: ruta donde se guardará el archivo descargado
    """

    if isinstance(file_id, str):
        file_id = ObjectId(file_id)

    archivo = fs.get(file_id)

    with open(ruta_salida, "wb") as salida:
        salida.write(archivo.read())

    return {
        "ok": True,
        "file_id": file_id,
        "ruta_salida": ruta_salida
    }


def eliminar_archivo(file_id):
    """
    Elimina un archivo de GridFS.
    """

    if isinstance(file_id, str):
        file_id = ObjectId(file_id)

    fs.delete(file_id)

    return {
        "ok": True,
        "file_id": file_id
    }


def obtener_info_archivo(file_id):
    """
    Obtiene la información de un archivo en GridFS.
    """

    if isinstance(file_id, str):
        file_id = ObjectId(file_id)

    archivo = fs.get(file_id)

    return {
        "file_id": archivo._id,
        "filename": archivo.filename,
        "length": archivo.length,
        "upload_date": archivo.upload_date,
        "metadata": getattr(archivo, "metadata", {})
    }