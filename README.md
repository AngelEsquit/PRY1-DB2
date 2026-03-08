
# Proyecto 1 - Base de Datos 2
## Sistema de Gestión de Pedidos y Reseñas de Restaurantes (MesaLista)

Este proyecto fue desarrollado como parte del curso **Base de Datos 2**.  
El objetivo es diseñar e implementar un sistema basado en **MongoDB** para la gestión de restaurantes, pedidos y reseñas, aplicando principios de modelado documental, agregaciones, índices y escalabilidad.

El sistema incluye una propuesta de interfaz llamada **MesaLista**, desarrollada con **React + Vite**, que permite visualizar y simular las operaciones principales del sistema.

---

# Integrantes

- **Angel Esteban Esquit Hernández** – 23221  
- **Anggelie Lizeth Velásquez Asencio** – 221181  
- **Mia Alejandra Fuentes Mérida** – 23775  

---

# Objetivo del proyecto

Diseñar un sistema completo para la gestión de restaurantes utilizando MongoDB que permita:

- Registrar restaurantes
- Administrar artículos de menú
- Gestionar usuarios
- Crear y consultar órdenes
- Registrar reseñas
- Analizar datos mediante agregaciones
- Optimizar consultas con índices
- Diseñar una estrategia de escalabilidad

---

# Tecnologías utilizadas

## Backend / Base de datos

- MongoDB Atlas
- Python
- PyMongo
- Faker
- python-dotenv

## Frontend

- React
- Vite
- React Router
- CSS

---

# Estructura del proyecto

```

PRY1-DB2/
│
├── crud/
│   ├── create.py
│   ├── read.py
│   ├── update.py
│   └── delete.py
│
├── Comparacion indices/
│
├── Frontend/
│   └── MesaLista/
│       ├── public/
│       ├── src/
│       │   ├── components/
│       │   ├── context/
│       │   ├── data/
│       │   ├── pages/
│       │   ├── styles/
│       │   ├── App.jsx
│       │   └── main.jsx
│       ├── index.html
│       ├── package.json
│       └── vite.config.js
│
├── requirements.txt
└── README.md

```

---

# Instalación de dependencias

## Backend

Instalar dependencias de Python:

```

pip install -r requirements.txt

```

Contenido del archivo:

```

pymongo>=4.6.0
dnspython>=2.6.1
Faker>=24.0.0
python-dotenv

```

---

# Ejecución del frontend

Entrar a la carpeta del frontend:

```

cd Frontend/MesaLista

```

Instalar dependencias:

```

npm install

```

Ejecutar el servidor de desarrollo:

```

npm run dev

```

Abrir en el navegador:

```

[http://localhost:5173](http://localhost:5173)

```

---

# Funcionalidades implementadas (Fase 1)

El frontend actualmente simula las funcionalidades principales del sistema utilizando datos mock.

## Navegación

El sistema cuenta con las siguientes páginas:

- Inicio
- Restaurantes
- Órdenes
- Reseñas
- Carrito

## Funcionalidades disponibles

### Restaurantes
- Visualización de restaurantes
- Búsqueda de restaurantes
- Página de detalle de restaurante
- Visualización del menú

### Carrito
- Agregar productos al carrito
- Seleccionar cantidad mediante modal
- Visualizar productos agregados
- Calcular total del pedido

### Órdenes
- Visualización de órdenes simuladas
- Detalle de órdenes

### Reseñas
- Visualización de reseñas
- Sistema de estrellas
- Formulario para crear reseñas

### Interfaz
- Navbar con navegación
- Indicador de carrito
- Modal para agregar productos
- Diseño responsive básico

---

# Modelado de datos en MongoDB

El sistema considera las siguientes colecciones principales:

- usuarios
- restaurantes
- menu_items
- ordenes
- reseñas

## Estrategia de modelado

Se utilizó una combinación de:

### Embedding

Para datos que se consultan juntos y deben conservarse históricamente.

Ejemplo:

```

orden.items[]

```

### Referencing

Para entidades reutilizables.

Ejemplo:

```

orden.usuario_id
orden.restaurante_id
reseña.restaurante_id

```

---

# Índices propuestos

El sistema contempla el uso de los siguientes índices:

- Índice simple
- Índice compuesto
- Índice multikey
- Índice geoespacial
- Índice de texto

Estos índices permiten optimizar consultas como:

- búsqueda de restaurantes
- consultas por usuario
- órdenes por fecha
- búsqueda por categoría
- consultas geográficas

---

# Aggregation Framework

El proyecto contempla el uso de pipelines de agregación para obtener información analítica como:

- platillos más vendidos
- restaurantes mejor calificados
- horas pico de pedidos
- promedio de reseñas

---

# Transacciones

Se consideran transacciones para garantizar consistencia en operaciones como:

- creación de órdenes
- actualización de puntos del usuario
- eliminación de usuarios y sus datos asociados

---

# Escalabilidad

La colección candidata para **sharding** es:

```

ordenes

```

### Shard Key propuesta

```

{ restaurante_id: 1, fecha: -1 }

```

Esto permite:

- distribuir carga de escritura
- evitar hotspots
- mejorar consultas por rango de fechas
- escalar horizontalmente el sistema


