from datetime import datetime
from bson import ObjectId

from crud.common import get_db, load_dotenv_file
from crud.create import (
    crear_usuario,
    crear_restaurante,
    crear_articulo_menu,
    crear_orden,
    crear_resena,
)
from crud.read import (
    buscar_restaurantes_por_nombre,
    buscar_restaurantes_por_tipo,
    buscar_usuarios_por_tipo,
    buscar_ordenes_por_estado,
    buscar_ordenes_por_rango_fechas,
    buscar_resenas_por_calificacion,
    obtener_nombres_restaurantes,
    obtener_datos_basicos_usuario,
    obtener_resumen_orden,
    ordenes_mas_recientes,
    restaurantes_por_nombre_ascendente,
    mejores_calificaciones,
    listar_restaurantes_paginados,
    listar_ordenes_usuario,
    ordenes_con_detalles_completos,
    articulos_con_restaurante,
    resenas_con_usuario_y_restaurante,
    historial_completo_usuario,
)
from crud.update import (
    actualizar_telefono_restaurante,
    actualizar_email_usuario,
    cambiar_estado_orden,
    actualizar_precio_articulo,
    desactivar_usuarios_inactivos,
    aplicar_descuento_por_categoria,
    marcar_ordenes_anticuadas,
    actualizar_direccion_restaurante,
)
from crud.delete import (
    eliminar_resena,
    eliminar_articulo_menu,
    eliminar_usuario,
    limpiar_resenas_antiguas,
    eliminar_usuarios_inactivos,
    limpiar_ordenes_canceladas,
)
from aggregations.aggregations import (
    platillos_mas_vendidos_mes,
    platillo_top_por_restaurante_en_mes,
    restaurantes_mejor_calificados,
    horas_pico_restaurante,
    ventas_por_restaurante,
    promedio_gasto_por_usuario,
    usuarios_activos_por_tipo,
)
from arrays.arrays import (
    agregar_preferencia_usuario,
    eliminar_preferencia_usuario,
    agregar_horario_restaurante,
    agregar_respuesta_resena,
    eliminar_respuesta_resena,
)
from gridfs_utils.gridfs_utils import (
    subir_archivo,
    listar_archivos,
    descargar_archivo,
    eliminar_archivo,
    obtener_info_archivo,
)
from transactions.transactions import (
    crear_orden_y_actualizar_puntos,
    eliminar_usuario_con_dependencias,
)
from comparacion_indices.comparacion_indices import presentacion_indices


# =========================
# HELPERS
# =========================

def pausar():
    input("\nPresiona Enter para continuar...")


def pedir_texto(msg, ejemplo=None, requerido=True):
    while True:
        prompt = msg
        if ejemplo:
            prompt += f" | Ejemplo: {ejemplo}"
        prompt += ": "

        valor = input(prompt).strip()

        if valor or not requerido:
            return valor

        print("Este campo no puede ir vacío.")


def pedir_entero(msg, minimo=None, maximo=None, ejemplo=None):
    while True:
        try:
            prompt = msg
            if ejemplo:
                prompt += f" | Ejemplo: {ejemplo}"
            prompt += ": "

            valor = int(input(prompt).strip())

            if minimo is not None and valor < minimo:
                print(f"El valor debe ser mayor o igual a {minimo}.")
                continue

            if maximo is not None and valor > maximo:
                print(f"El valor debe ser menor o igual a {maximo}.")
                continue

            return valor
        except ValueError:
            print("Debes ingresar un número entero válido.")


def pedir_decimal(msg, ejemplo=None):
    while True:
        try:
            prompt = msg
            if ejemplo:
                prompt += f" | Ejemplo: {ejemplo}"
            prompt += ": "
            return float(input(prompt).strip())
        except ValueError:
            print("Debes ingresar un número válido. Ejemplo: 45.50")


def pedir_lista(msg, ejemplo=None):
    valor = input(
        f"{msg}" + (f" | Ejemplo: {ejemplo}" if ejemplo else "") + ": "
    ).strip()

    if not valor:
        return []

    return [x.strip() for x in valor.split(",") if x.strip()]


def pedir_fecha_inicio():
    while True:
        valor = input("Fecha inicio en formato YYYY-MM-DD | Ejemplo: 2026-03-01: ").strip()
        try:
            return datetime.fromisoformat(valor + "T00:00:00")
        except ValueError:
            print("Fecha inválida. Usa el formato YYYY-MM-DD.")


def pedir_fecha_fin():
    while True:
        valor = input("Fecha fin en formato YYYY-MM-DD | Ejemplo: 2026-03-31: ").strip()
        try:
            return datetime.fromisoformat(valor + "T23:59:59")
        except ValueError:
            print("Fecha inválida. Usa el formato YYYY-MM-DD.")


def mostrar_ejemplos_ids(db, coleccion_nombre, limite=3):
    print(f"\nEjemplos disponibles en la colección '{coleccion_nombre}':")
    coleccion = getattr(db, coleccion_nombre)
    docs = list(coleccion.find().limit(limite))

    if not docs:
        print("No hay documentos disponibles.")
        return

    for i, doc in enumerate(docs, start=1):
        descripcion = []

        if "nombre" in doc:
            descripcion.append(f"nombre={doc['nombre']}")
        if "apellido" in doc:
            descripcion.append(f"apellido={doc['apellido']}")
        if "email" in doc:
            descripcion.append(f"email={doc['email']}")
        if "estado" in doc:
            descripcion.append(f"estado={doc['estado']}")
        if "categoria" in doc:
            descripcion.append(f"categoria={doc['categoria']}")
        if "titulo" in doc:
            descripcion.append(f"titulo={doc['titulo']}")

        extra = " | ".join(descripcion) if descripcion else "sin descripción"
        print(f"{i}. _id={doc['_id']} | {extra}")


def pedir_objectid(msg, ejemplo=None, db=None, coleccion_sugerida=None):
    while True:
        if db is not None and coleccion_sugerida:
            ver = input(
                f"¿Deseas ver ejemplos de IDs de la colección '{coleccion_sugerida}'? (s/n): "
            ).strip().lower()
            if ver == "s":
                mostrar_ejemplos_ids(db, coleccion_sugerida)

        valor = input(
            f"{msg}" + (f" | Ejemplo: {ejemplo}" if ejemplo else "") + ": "
        ).strip()

        try:
            return ObjectId(valor)
        except Exception:
            print("Debes ingresar un ObjectId válido de MongoDB.")


# =========================
# MENÚS
# =========================

def print_menu():
    print("\n" + "=" * 70)
    print("SISTEMA DE GESTIÓN DE PEDIDOS Y RESEÑAS - BACKEND")
    print("=" * 70)
    print("1. CRUD - Create")
    print("2. CRUD - Read")
    print("3. CRUD - Update")
    print("4. CRUD - Delete")
    print("5. Aggregations")
    print("6. Manejo de Arrays")
    print("7. Transacciones")
    print("8. GridFS")
    print("9. Comparación de índices")
    print("0. Salir")
    print("=" * 70)


def print_submenu(title, options):
    print(f"\n--- {title} ---")
    for key, value in options.items():
        print(f"{key}. {value}")
    print("0. Volver")


# =========================
# CRUD CREATE
# =========================

def crud_create_menu(db):
    opciones = {
        "1": "Crear usuario",
        "2": "Crear restaurante",
        "3": "Crear artículo de menú",
        "4": "Crear orden",
        "5": "Crear reseña",
    }

    while True:
        print_submenu("CRUD - CREATE", opciones)
        op = input("Selecciona una opción: ").strip()

        try:
            if op == "1":
                print("\nCrear usuario")
                print("Ingresa los datos personales y la dirección del usuario.\n")

                user_id = crear_usuario(
                    nombre=pedir_texto("Nombre del usuario"),
                    apellido=pedir_texto("Apellido del usuario"),
                    email=pedir_texto("Correo electrónico", "user@email.com"),
                    telefono=pedir_texto("Teléfono", "5555-1234"),
                    direccion={
                        "calle": pedir_texto("Calle o avenida", "4ta avenida 10-25"),
                        "ciudad": pedir_texto("Ciudad", "Guatemala"),
                        "codigo_postal": pedir_texto("Código postal", "01010"),
                    },
                    db=db,
                )
                print("Usuario creado:", user_id)
                pausar()

            elif op == "2":
                print("\nCrear restaurante")
                print("Debes ingresar nombre, descripción, dirección, ubicación y contacto.")
                print("Ubicación ejemplo Guatemala: Longitud -90.5069 | Latitud 14.6349\n")

                rest_id = crear_restaurante(
                    {
                        "nombre": pedir_texto("Nombre del restaurante", "Mesa del Lago"),
                        "descripcion": pedir_texto(
                            "Descripción del restaurante",
                            "Comida italiana con vista al lago"
                        ),
                        "tipo_comida": pedir_lista(
                            "Tipos de comida separados por coma",
                            "Italiana, Pasta, Pizza"
                        ),
                        "direccion": {
                            "calle": pedir_texto("Zona y calle/avenida", "Zona 10, 5a avenida"),
                            "ciudad": pedir_texto("Ciudad", "Guatemala"),
                            "codigo_postal": pedir_texto("Código postal", "01010"),
                        },
                        "ubicacion": {
                            "type": "Point",
                            "coordinates": [
                                pedir_decimal("Longitud", "-90.5069"),
                                pedir_decimal("Latitud", "14.6349"),
                            ],
                        },
                        "horario": {
                            "lunes": {"abierto": True, "desde": "08:00", "hasta": "20:00"}
                        },
                        "telefono": pedir_texto("Teléfono del restaurante", "2222-3333"),
                        "email": pedir_texto("Correo del restaurante", "contacto@mesa.com"),
                    },
                    db=db,
                )
                print("Restaurante creado:", rest_id)
                pausar()

            elif op == "3":
                print("\nCrear artículo de menú")
                print("Necesitas el ID del restaurante al que pertenece el artículo.\n")

                art_id = crear_articulo_menu(
                    restaurante_id=pedir_objectid(
                        "ID del restaurante dueño del artículo",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="restaurantes",
                    ),
                    datos_articulo={
                        "nombre": pedir_texto("Nombre del artículo", "Pizza Margarita"),
                        "descripcion": pedir_texto(
                            "Descripción del artículo",
                            "Pizza con queso, tomate y albahaca"
                        ),
                        "categoria": pedir_texto("Categoría", "Pizza"),
                        "precio": pedir_texto("Precio en quetzales", "65.50"),
                        "ingredientes": pedir_lista(
                            "Ingredientes separados por coma",
                            "queso, tomate, albahaca"
                        ),
                        "opciones_personalizacion": [],
                        "tiempo_preparacion": pedir_entero(
                            "Tiempo de preparación en minutos",
                            minimo=1,
                            ejemplo="20"
                        ),
                    },
                    db=db,
                )
                print("Artículo creado:", art_id)
                pausar()

            elif op == "4":
                print("\nCrear orden")
                print("Debes ingresar IDs válidos de usuario, restaurante y artículo.\n")

                usuario_id = pedir_objectid(
                    "ID del usuario",
                    "64f123abc456def789012345",
                    db=db,
                    coleccion_sugerida="usuarios",
                )
                restaurante_id = pedir_objectid(
                    "ID del restaurante",
                    "64f123abc456def789012346",
                    db=db,
                    coleccion_sugerida="restaurantes",
                )
                articulo_id = pedir_objectid(
                    "ID del artículo del menú",
                    "64f123abc456def789012347",
                    db=db,
                    coleccion_sugerida="articulos_menu",
                )
                cantidad = pedir_entero("Cantidad del artículo", minimo=1, ejemplo="2")

                orden = crear_orden(
                    usuario_id=usuario_id,
                    restaurante_id=restaurante_id,
                    items_seleccionados=[
                        {
                            "articulo_id": articulo_id,
                            "cantidad": cantidad,
                            "personalizaciones": [],
                        }
                    ],
                    metodo_pago=pedir_texto(
                        "Método de pago",
                        "efectivo o tarjeta"
                    ),
                    db=db,
                )
                print("Orden creada:", orden["_id"])
                pausar()

            elif op == "5":
                print("\nCrear reseña")
                print("La calificación debe estar entre 1 y 5.\n")

                resena_id = crear_resena(
                    usuario_id=pedir_objectid(
                        "ID del usuario que reseña",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="usuarios",
                    ),
                    restaurante_id=pedir_objectid(
                        "ID del restaurante reseñado",
                        "64f123abc456def789012346",
                        db=db,
                        coleccion_sugerida="restaurantes",
                    ),
                    calificacion=pedir_entero("Calificación", minimo=1, maximo=5, ejemplo="4"),
                    titulo=pedir_texto("Título de la reseña", "Muy buen servicio"),
                    comentario=pedir_texto(
                        "Comentario de la reseña",
                        "La comida estuvo deliciosa y llegó rápido"
                    ),
                    db=db,
                )
                print("Reseña creada:", resena_id)
                pausar()

            elif op == "0":
                break
            else:
                print("Opción no válida.")
        except Exception as e:
            print("Error:", e)
            pausar()


# =========================
# CRUD READ
# =========================

def crud_read_menu(db):
    opciones = {
        "1": "Buscar restaurantes por nombre",
        "2": "Buscar restaurantes por tipo",
        "3": "Buscar usuarios por tipo",
        "4": "Buscar órdenes por estado",
        "5": "Buscar órdenes por rango de fechas",
        "6": "Buscar reseñas por calificación",
        "7": "Obtener nombres de restaurantes",
        "8": "Obtener datos básicos de usuario",
        "9": "Obtener resumen de orden",
        "10": "Órdenes más recientes",
        "11": "Restaurantes por nombre ascendente",
        "12": "Mejores calificaciones",
        "13": "Listar restaurantes paginados",
        "14": "Listar órdenes de usuario",
        "15": "Orden con detalles completos",
        "16": "Artículo con restaurante",
        "17": "Reseña con usuario y restaurante",
        "18": "Historial completo de usuario",
    }

    while True:
        print_submenu("CRUD - READ", opciones)
        op = input("Selecciona una opción: ").strip()

        try:
            if op == "1":
                print(buscar_restaurantes_por_nombre(
                    pedir_texto("Nombre o parte del nombre del restaurante", "Lago"),
                    db=db
                ))
                pausar()

            elif op == "2":
                print(buscar_restaurantes_por_tipo(
                    pedir_texto("Tipo de comida", "Italiana"),
                    db=db
                ))
                pausar()

            elif op == "3":
                print(buscar_usuarios_por_tipo(
                    pedir_texto("Tipo de usuario", "vip"),
                    skip=pedir_entero("Skip (usuarios a omitir)", minimo=0, ejemplo="0"),
                    limit=pedir_entero("Limit (máximo de usuarios)", minimo=1, ejemplo="20"),
                    db=db
                ))
                pausar()

            elif op == "4":
                print(buscar_ordenes_por_estado(
                    pedir_texto("Estado de la orden", "pendiente"),
                    db=db
                ))
                pausar()

            elif op == "5":
                inicio = pedir_fecha_inicio()
                fin = pedir_fecha_fin()
                print(buscar_ordenes_por_rango_fechas(inicio, fin, db=db))
                pausar()

            elif op == "6":
                minimo = pedir_entero("Calificación mínima", minimo=1, maximo=5, ejemplo="3")
                maximo = pedir_entero("Calificación máxima", minimo=1, maximo=5, ejemplo="5")
                print(buscar_resenas_por_calificacion(minimo, maximo, db=db))
                pausar()

            elif op == "7":
                print(obtener_nombres_restaurantes(db=db))
                pausar()

            elif op == "8":
                print(obtener_datos_basicos_usuario(
                    pedir_objectid(
                        "ID del usuario",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="usuarios",
                    ),
                    db=db
                ))
                pausar()

            elif op == "9":
                print(obtener_resumen_orden(
                    pedir_objectid(
                        "ID de la orden",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="ordenes",
                    ),
                    db=db
                ))
                pausar()

            elif op == "10":
                print(ordenes_mas_recientes(
                    pedir_entero("Cantidad de órdenes a mostrar", minimo=1, ejemplo="5"),
                    db=db
                ))
                pausar()

            elif op == "11":
                print(restaurantes_por_nombre_ascendente(
                    skip=pedir_entero("Skip (restaurantes a omitir)", minimo=0, ejemplo="0"),
                    limit=pedir_entero("Limit (máximo de restaurantes)", minimo=1, ejemplo="10"),
                    sort_dir=pedir_entero("Dirección: 1=Ascendente, -1=Descendente", minimo=-1, maximo=1, ejemplo="1"),
                    db=db
                ))
                pausar()

            elif op == "12":
                print(mejores_calificaciones(
                    pedir_entero("Cantidad de resultados", minimo=1, ejemplo="5"),
                    db=db
                ))
                pausar()

            elif op == "13":
                pagina = pedir_entero("Número de página", minimo=1, ejemplo="1")
                por_pagina = pedir_entero("Cantidad por página", minimo=1, ejemplo="10")
                print(listar_restaurantes_paginados(pagina, por_pagina, db=db))
                pausar()

            elif op == "14":
                usuario_id = pedir_objectid(
                    "ID del usuario",
                    "64f123abc456def789012345",
                    db=db,
                    coleccion_sugerida="usuarios",
                )
                pagina = pedir_entero("Número de página", minimo=1, ejemplo="1")
                por_pagina = pedir_entero("Cantidad por página", minimo=1, ejemplo="10")
                print(listar_ordenes_usuario(usuario_id, pagina, por_pagina, db=db))
                pausar()

            elif op == "15":
                print(ordenes_con_detalles_completos(
                    pedir_objectid(
                        "ID de la orden",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="ordenes",
                    ),
                    db=db
                ))
                pausar()

            elif op == "16":
                print(articulos_con_restaurante(
                    pedir_objectid(
                        "ID del artículo",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="articulos_menu",
                    ),
                    db=db
                ))
                pausar()

            elif op == "17":
                print(resenas_con_usuario_y_restaurante(
                    pedir_objectid(
                        "ID de la reseña",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="resenas",
                    ),
                    db=db
                ))
                pausar()

            elif op == "18":
                print(historial_completo_usuario(
                    pedir_objectid(
                        "ID del usuario",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="usuarios",
                    ),
                    db=db
                ))
                pausar()

            elif op == "0":
                break
            else:
                print("Opción no válida.")
        except Exception as e:
            print("Error:", e)
            pausar()


# =========================
# CRUD UPDATE
# =========================

def crud_update_menu(db):
    opciones = {
        "1": "Actualizar teléfono de restaurante",
        "2": "Actualizar email de usuario",
        "3": "Cambiar estado de orden",
        "4": "Actualizar precio de artículo",
        "5": "Desactivar usuarios inactivos",
        "6": "Aplicar descuento por categoría",
        "7": "Actualizar dirección de restaurante",
        "8": "Marcar órdenes antiguas",
    }

    while True:
        print_submenu("CRUD - UPDATE", opciones)
        op = input("Selecciona una opción: ").strip()

        try:
            if op == "1":
                print(actualizar_telefono_restaurante(
                    pedir_objectid(
                        "ID del restaurante",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="restaurantes",
                    ),
                    pedir_texto("Nuevo teléfono", "2222-3333"),
                    db=db
                ))
                pausar()

            elif op == "2":
                print(actualizar_email_usuario(
                    pedir_objectid(
                        "ID del usuario",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="usuarios",
                    ),
                    pedir_texto("Nuevo correo electrónico", "nuevo@email.com"),
                    db=db
                ))
                pausar()

            elif op == "3":
                print("Estados sugeridos: pendiente, en_preparacion, entregada, cancelada")
                print(cambiar_estado_orden(
                    pedir_objectid(
                        "ID de la orden",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="ordenes",
                    ),
                    pedir_texto("Nuevo estado de la orden", "entregada"),
                    db=db
                ))
                pausar()

            elif op == "4":
                print(actualizar_precio_articulo(
                    pedir_objectid(
                        "ID del artículo",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="articulos_menu",
                    ),
                    pedir_texto("Nuevo precio del artículo", "75.00"),
                    db=db
                ))
                pausar()

            elif op == "5":
                print(desactivar_usuarios_inactivos(
                    pedir_entero("Meses de inactividad", minimo=1, ejemplo="6"),
                    db=db
                ))
                pausar()

            elif op == "6":
                print(aplicar_descuento_por_categoria(
                    pedir_texto("Categoría a modificar", "Pizza"),
                    pedir_decimal("Porcentaje de descuento", "10"),
                    db=db
                ))
                pausar()

            elif op == "7":
                print(actualizar_direccion_restaurante(
                    pedir_objectid(
                        "ID del restaurante",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="restaurantes",
                    ),
                    pedir_texto("Nueva calle", "5a avenida 10-25, Zona 10"),
                    pedir_texto("Nueva ciudad", "Guatemala"),
                    pedir_texto("Nuevo código postal", "01010"),
                    db=db
                ))
                pausar()

            elif op == "8":
                print(marcar_ordenes_anticuadas(db=db))
                pausar()

            elif op == "0":
                break
            else:
                print("Opción no válida.")
        except Exception as e:
            print("Error:", e)
            pausar()


# =========================
# CRUD DELETE
# =========================

def crud_delete_menu(db):
    opciones = {
        "1": "Eliminar reseña",
        "2": "Eliminar artículo de menú",
        "3": "Eliminar usuario",
        "4": "Limpiar reseñas antiguas",
        "5": "Eliminar usuarios inactivos",
        "6": "Limpiar órdenes canceladas",
    }

    while True:
        print_submenu("CRUD - DELETE", opciones)
        op = input("Selecciona una opción: ").strip()

        try:
            if op == "1":
                print(eliminar_resena(
                    pedir_objectid(
                        "ID de la reseña a eliminar",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="resenas",
                    ),
                    db=db
                ))
                pausar()

            elif op == "2":
                print(eliminar_articulo_menu(
                    pedir_objectid(
                        "ID del artículo a eliminar",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="articulos_menu",
                    ),
                    db=db
                ))
                pausar()

            elif op == "3":
                print(eliminar_usuario(
                    pedir_objectid(
                        "ID del usuario a eliminar",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="usuarios",
                    ),
                    db=db
                ))
                pausar()

            elif op == "4":
                print(limpiar_resenas_antiguas(
                    pedir_entero("Eliminar reseñas con más de cuántos años", minimo=1, ejemplo="2"),
                    db=db
                ))
                pausar()

            elif op == "5":
                print(eliminar_usuarios_inactivos(db=db))
                pausar()

            elif op == "6":
                print(limpiar_ordenes_canceladas(db=db))
                pausar()

            elif op == "0":
                break
            else:
                print("Opción no válida.")
        except Exception as e:
            print("Error:", e)
            pausar()


# =========================
# AGGREGATIONS
# =========================

def aggregations_menu(db):
    opciones = {
        "1": "Platillos más vendidos del mes",
        "2": "Restaurantes mejor calificados",
        "3": "Horas pico de restaurante",
        "4": "Ventas por restaurante",
        "5": "Promedio de gasto por usuario",
        "6": "Usuarios activos por tipo",
    }

    while True:
        print_submenu("AGGREGATIONS", opciones)
        op = input("Selecciona una opción: ").strip()

        try:
            if op == "1":
                print(platillo_top_por_restaurante_en_mes(
                    pedir_entero("Año de consulta", minimo=2000, ejemplo="2026"),
                    pedir_entero("Mes de consulta", minimo=1, maximo=12, ejemplo="3")
                ))
                pausar()

            elif op == "2":
                print(restaurantes_mejor_calificados(
                    pedir_entero("Mínimo de reseñas requeridas", minimo=1, ejemplo="5"),
                    pedir_entero("Cantidad de resultados", minimo=1, ejemplo="5")
                ))
                pausar()

            elif op == "3":
                print(horas_pico_restaurante(
                    pedir_objectid(
                        "ID del restaurante",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="restaurantes",
                    )
                ))
                pausar()

            elif op == "4":
                print(ventas_por_restaurante())
                pausar()

            elif op == "5":
                print(promedio_gasto_por_usuario(
                    pedir_entero("Cantidad de usuarios a mostrar", minimo=1, ejemplo="5")
                ))
                pausar()

            elif op == "6":
                print(usuarios_activos_por_tipo())
                pausar()

            elif op == "0":
                break
            else:
                print("Opción no válida.")
        except Exception as e:
            print("Error:", e)
            pausar()


# =========================
# ARRAYS
# =========================

def arrays_menu(db):
    opciones = {
        "1": "Agregar preferencia a usuario",
        "2": "Eliminar preferencia de usuario",
        "3": "Agregar horario a restaurante",
        "4": "Agregar respuesta a reseña",
        "5": "Eliminar respuesta de reseña",
    }

    while True:
        print_submenu("MANEJO DE ARRAYS", opciones)
        op = input("Selecciona una opción: ").strip()

        try:
            if op == "1":
                print(agregar_preferencia_usuario(
                    pedir_objectid(
                        "ID del usuario",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="usuarios",
                    ),
                    pedir_texto("Nueva preferencia a agregar", "Italiana")
                ))
                pausar()

            elif op == "2":
                print(eliminar_preferencia_usuario(
                    pedir_objectid(
                        "ID del usuario",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="usuarios",
                    ),
                    pedir_texto("Preferencia a eliminar", "Italiana")
                ))
                pausar()

            elif op == "3":
                print("\nAgregar horario a restaurante")
                print("Formato de hora sugerido: HH:MM | Ejemplo: 08:00\n")

                nuevo_horario = {
                    "dia": pedir_texto("Día", "martes"),
                    "desde": pedir_texto("Hora de inicio", "08:00"),
                    "hasta": pedir_texto("Hora de cierre", "20:00")
                }
                print(agregar_horario_restaurante(
                    pedir_objectid(
                        "ID del restaurante",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="restaurantes",
                    ),
                    nuevo_horario
                ))
                pausar()

            elif op == "4":
                print(agregar_respuesta_resena(
                    pedir_objectid(
                        "ID de la reseña",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="resenas",
                    ),
                    {
                        "texto": pedir_texto("Texto de la respuesta", "Gracias por tu comentario"),
                        "fecha": datetime.utcnow()
                    }
                ))
                pausar()

            elif op == "5":
                print(eliminar_respuesta_resena(
                    pedir_objectid(
                        "ID de la reseña",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="resenas",
                    ),
                    pedir_texto("Texto exacto de la respuesta a eliminar", "Gracias por tu comentario")
                ))
                pausar()

            elif op == "0":
                break
            else:
                print("Opción no válida.")
        except Exception as e:
            print("Error:", e)
            pausar()


# =========================
# TRANSACCIONES
# =========================

def transactions_menu(db):
    opciones = {
        "1": "Crear orden y actualizar puntos",
        "2": "Eliminar usuario con dependencias",
    }

    while True:
        print_submenu("TRANSACCIONES", opciones)
        op = input("Selecciona una opción: ").strip()

        try:
            if op == "1":
                print("\nTransacción: crear orden y actualizar puntos")
                print("Debes usar un artículo que pertenezca al restaurante ingresado.\n")

                usuario_id = pedir_objectid(
                    "ID del usuario",
                    "64f123abc456def789012345",
                    db=db,
                    coleccion_sugerida="usuarios",
                )
                restaurante_id = pedir_objectid(
                    "ID del restaurante",
                    "64f123abc456def789012346",
                    db=db,
                    coleccion_sugerida="restaurantes",
                )
                articulo_id = pedir_objectid(
                    "ID del artículo del menú",
                    "64f123abc456def789012347",
                    db=db,
                    coleccion_sugerida="articulos_menu",
                )
                cantidad = pedir_entero("Cantidad del artículo", minimo=1, ejemplo="2")
                metodo_pago = pedir_texto("Método de pago", "efectivo")

                print(crear_orden_y_actualizar_puntos(
                    usuario_id=usuario_id,
                    restaurante_id=restaurante_id,
                    items=[{"articulo_id": articulo_id, "cantidad": cantidad}],
                    metodo_pago=metodo_pago,
                ))
                pausar()

            elif op == "2":
                print("\nTransacción: eliminar usuario con sus órdenes y reseñas")
                print("Esta acción borra al usuario y sus dependencias asociadas.\n")

                print(eliminar_usuario_con_dependencias(
                    pedir_objectid(
                        "ID del usuario a eliminar",
                        "64f123abc456def789012345",
                        db=db,
                        coleccion_sugerida="usuarios",
                    )
                ))
                pausar()

            elif op == "0":
                break
            else:
                print("Opción no válida.")
        except Exception as e:
            print("Error:", e)
            pausar()


# =========================
# GRIDFS
# =========================

def gridfs_menu():
    opciones = {
        "1": "Subir archivo",
        "2": "Listar archivos",
        "3": "Descargar archivo",
        "4": "Eliminar archivo",
        "5": "Obtener info de archivo",
    }

    while True:
        print_submenu("GRIDFS", opciones)
        op = input("Selecciona una opción: ").strip()

        try:
            if op == "1":
                print("\nSubir archivo a GridFS")
                print("Debes ingresar la ruta completa del archivo en tu computadora.")
                print(r"Ejemplo Windows: C:\Users\angge\Downloads\foto.jpg")
                print()

                ruta = pedir_texto("Ruta del archivo")
                nombre = pedir_texto(
                    "Nombre para guardar en GridFS (deja vacío para automático)",
                    "foto_restaurante.jpg",
                    requerido=False
                )
                nombre = nombre if nombre else None
                print(subir_archivo(ruta, nombre_archivo=nombre))
                pausar()

            elif op == "2":
                print(listar_archivos())
                pausar()

            elif op == "3":
                print("\nDescargar archivo desde GridFS")
                print(r"Ejemplo de salida: C:\Users\angge\Downloads\archivo_descargado.jpg")
                print()

                print(descargar_archivo(
                    input("ID del archivo en GridFS: ").strip(),
                    pedir_texto("Ruta donde se guardará el archivo descargado")
                ))
                pausar()

            elif op == "4":
                print(eliminar_archivo(
                    input("ID del archivo a eliminar en GridFS: ").strip()
                ))
                pausar()

            elif op == "5":
                print(obtener_info_archivo(
                    input("ID del archivo en GridFS: ").strip()
                ))
                pausar()

            elif op == "0":
                break
            else:
                print("Opción no válida.")
        except Exception as e:
            print("Error:", e)
            pausar()


# =========================
# MAIN
# =========================

def main():
    load_dotenv_file()
    db = get_db()

    print(f"Conectado a la base de datos: {db.name}")

    while True:
        print_menu()
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            crud_create_menu(db)
        elif opcion == "2":
            crud_read_menu(db)
        elif opcion == "3":
            crud_update_menu(db)
        elif opcion == "4":
            crud_delete_menu(db)
        elif opcion == "5":
            aggregations_menu(db)
        elif opcion == "6":
            arrays_menu(db)
        elif opcion == "7":
            transactions_menu(db)
        elif opcion == "8":
            gridfs_menu()
        elif opcion == "9":
            presentacion_indices(db)
            pausar()
        elif opcion == "0":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()