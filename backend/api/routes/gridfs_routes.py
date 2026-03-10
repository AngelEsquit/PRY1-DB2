from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import Response
from bson import ObjectId
from gridfs import GridFS

from crud.common import db

router = APIRouter(prefix="/gridfs", tags=["GridFS"])
fs = GridFS(db)


@router.get("/files")
def list_files():
    result = []
    for archivo in fs.find():
        result.append({
            "file_id": str(archivo._id),
            "filename": archivo.filename,
            "length": archivo.length,
            "upload_date": archivo.upload_date.isoformat() if archivo.upload_date else None,
            "metadata": getattr(archivo, "metadata", {}),
        })
    return result


@router.post("/files")
def upload_file(file: UploadFile = File(...)):
    try:
        content = file.file.read()
        file_id = fs.put(
            content,
            filename=file.filename,
            contentType=file.content_type or "application/octet-stream",
        )
        return {"ok": True, "file_id": str(file_id), "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/files/{file_id}/info")
def get_file_info(file_id: str):
    try:
        oid = ObjectId(file_id)
        archivo = fs.get(oid)
        return {
            "file_id": str(archivo._id),
            "filename": archivo.filename,
            "length": archivo.length,
            "upload_date": archivo.upload_date.isoformat() if archivo.upload_date else None,
            "metadata": getattr(archivo, "metadata", {}),
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/files/{file_id}/download")
def download_file(file_id: str):
    try:
        oid = ObjectId(file_id)
        archivo = fs.get(oid)
        data = archivo.read()
        return Response(
            content=data,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{archivo.filename}"'},
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/files/{file_id}")
def delete_file(file_id: str):
    try:
        oid = ObjectId(file_id)
        fs.delete(oid)
        return {"ok": True, "file_id": file_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
