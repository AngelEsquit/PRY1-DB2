# Proyecto 1 - Base de Datos 2
## MesaLista: Sistema de Gestion de Pedidos y Resenas

Aplicacion fullstack para gestionar restaurantes, menu, ordenes, usuarios y resenas sobre MongoDB.

## Integrantes
- Angel Esteban Esquit Hernandez - 23221
- Anggelie Lizeth Velasquez Asencio - 221181
- Mia Alejandra Fuentes Merida - 23775

## Stack
- Backend: FastAPI, PyMongo, Python
- Base de datos: MongoDB Atlas
- Frontend: React + Vite

## Estructura minima
- `backend/` API FastAPI y logica MongoDB
- `Frontend/MesaLista/` app React
- `requirements.txt` dependencias backend

---

## Requisitos
- Python 3.11+
- Node.js 18+
- npm
- Acceso a MongoDB (Atlas o local)

---

## Configuracion del backend

### 1) Crear y activar entorno virtual (Windows)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 3) Configurar variables de entorno
Crear archivo `backend/.env` con:
```env
MONGO_URI = "mongodb+srv://user:123@basesdedatos2.0l9vfjv.mongodb.net/?appName=BasesDeDatos2"
MONGO_DB_NAME = "restaurantes_db"
```

Importante:
- El backend lee `backend/.env`.
- Si `MONGO_URI` no es valido, la API no podra consultar datos.

### 4) Ejecutar backend (recomendado desde raiz)
```powershell
python -m uvicorn api.app:app --reload --app-dir backend
```

Alternativa (si prefieres entrar a backend):
```powershell
cd backend
python -m uvicorn api.app:app --reload
```

Backend en:
- `http://127.0.0.1:8000`
- Docs Swagger: `http://127.0.0.1:8000/docs`

---

## Configuracion del frontend

### 1) Instalar dependencias
```powershell
cd Frontend/MesaLista
npm install
```

### 2) Ejecutar frontend
```powershell
npm run dev
```

Frontend en:
- `http://localhost:5173`

---

## Orden recomendado para correr el proyecto
1. Activar `.venv` e iniciar backend.
2. En otra terminal, iniciar frontend.
3. Abrir `http://localhost:5173`.

---

## Endpoints utiles para validar rapido
- `GET /` -> estado API
- `GET /restaurants/` -> lista restaurantes
- `GET /users/?tipo=premium` -> filtro por tipo
- `GET /orders/?estado=pendiente` -> filtro por estado

---

## Errores comunes y solucion

### Error: `Form data requires "python-multipart" to be installed`
Instala dependencias dentro del `.venv` y ejecuta con ese Python.

### Error: `No module named 'api'`
Estas corriendo desde raiz sin `--app-dir backend`.
Usa:
```powershell
python -m uvicorn api.app:app --reload --app-dir backend
```


