import argparse
import json
import logging
import os
import random
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Sequence, Tuple

from bson import Decimal128, ObjectId
from faker import Faker
from pymongo import ASCENDING, GEOSPHERE, MongoClient, TEXT
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import AutoReconnect, BulkWriteError, PyMongoError, ServerSelectionTimeoutError


# =========================
# Configuración principal
# =========================

RANDOM_SEED = 42
DEFAULT_DB_NAME = "restaurantes_db"
DEFAULT_STATS_FILE = "estadisticas_generacion.json"

COLLECTIONS = {
	"restaurantes": 1000,
	"usuarios": 5000,
	"articulos_menu": 15000,
	"ordenes": 60000,
	"resenas": 50000,
}

BATCH_SIZE = 1000
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2

TIPOS_COMIDA = [
	"Guatemalteca", "Italiana", "Pizza", "Pastas", "Mexicana", "Japonesa", "Asiática",
	"Hamburguesas", "Parrilla", "Vegana", "Vegetariana", "Mariscos", "Postres", "Cafetería",
	"Internacional", "Comida Rápida", "Saludable", "Panadería", "Fusión"
]

CATEGORIAS_MENU = ["Entrada", "Plato Principal", "Postre", "Bebida", "Acompañamiento"]

ESTADOS_ORDEN = [
	"pendiente", "confirmado", "en_preparacion", "en_camino", "entregado", "cancelado"
]
PESOS_ESTADOS_ORDEN = [5, 10, 10, 10, 60, 5]

METODOS_PAGO = ["efectivo", "tarjeta", "transferencia"]

TIPOS_USUARIO = ["regular", "premium", "vip"]
PESOS_TIPOS_USUARIO = [70, 20, 10]

CALIFICACIONES = [1, 2, 3, 4, 5]
PESOS_CALIFICACIONES = [5, 10, 20, 30, 35]

PERSONALIZACIONES_COMUNES = [
	"sin cebolla", "extra queso", "poco picante", "sin sal", "extra salsa",
	"sin gluten", "doble porción", "sin lactosa", "bien cocido", "término medio"
]

INGREDIENTES_BASE = [
	"pollo", "res", "cerdo", "queso", "tomate", "cebolla", "ajo", "pimienta", "chile",
	"maíz", "frijol", "arroz", "pasta", "albahaca", "orégano", "crema", "lechuga",
	"aguacate", "limón", "papas", "champiñones", "pan", "huevo", "camarón", "atún",
	"tofu", "espinaca", "zanahoria", "pepino", "aceite de oliva"
]

CIUDADES_GUATEMALA = [
	{"ciudad": "Ciudad de Guatemala", "lat": 14.6349, "lon": -90.5069, "cp": "01001"},
	{"ciudad": "Mixco", "lat": 14.6333, "lon": -90.6064, "cp": "01057"},
	{"ciudad": "Villa Nueva", "lat": 14.5269, "lon": -90.5875, "cp": "01064"},
	{"ciudad": "Antigua Guatemala", "lat": 14.5586, "lon": -90.7343, "cp": "03001"},
	{"ciudad": "Quetzaltenango", "lat": 14.8347, "lon": -91.5180, "cp": "09001"},
	{"ciudad": "Escuintla", "lat": 14.3050, "lon": -90.7850, "cp": "05001"},
	{"ciudad": "Cobán", "lat": 15.4700, "lon": -90.3700, "cp": "16001"},
	{"ciudad": "Puerto Barrios", "lat": 15.7278, "lon": -88.5944, "cp": "18001"},
	{"ciudad": "Chiquimula", "lat": 14.8000, "lon": -89.5500, "cp": "20001"},
	{"ciudad": "Huehuetenango", "lat": 15.3200, "lon": -91.4700, "cp": "13001"},
]

DAYS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]


@dataclass
class UsuarioRef:
	_id: ObjectId
	fecha_registro: datetime
	direccion: Dict
	tipo: str


@dataclass
class RestauranteRef:
	_id: ObjectId
	nombre: str
	direccion: Dict


@dataclass
class ArticuloRef:
	_id: ObjectId
	restaurante_id: ObjectId
	nombre: str
	precio: Decimal
	categoria: str


@dataclass
class OrdenRef:
	_id: ObjectId
	usuario_id: ObjectId
	restaurante_id: ObjectId
	fecha_pedido: datetime
	articulo_ids: List[ObjectId]


def configure_logging() -> None:
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S",
	)


def quantize_money(value: Decimal) -> Decimal:
	return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def to_decimal128(value: Decimal) -> Decimal128:
	return Decimal128(str(quantize_money(value)))


def random_date_within_years(years_back: int) -> datetime:
	now = datetime.utcnow()
	start = now - timedelta(days=365 * years_back)
	delta_seconds = int((now - start).total_seconds())
	return start + timedelta(seconds=random.randint(0, max(delta_seconds, 1)))


def jitter_coordinate(base: float, max_delta: float = 0.06) -> float:
	return round(base + random.uniform(-max_delta, max_delta), 6)


def generate_week_schedule() -> Dict[str, Dict[str, str]]:
	schedule = {}
	for day in DAYS:
		if random.random() < 0.08:
			schedule[day] = {"abierto": False}
			continue
		open_hour = random.choice([7, 8, 9, 10, 11])
		close_hour = random.choice([20, 21, 22, 23])
		if close_hour <= open_hour:
			close_hour = open_hour + 10
		schedule[day] = {
			"abierto": True,
			"desde": f"{open_hour:02d}:00",
			"hasta": f"{close_hour:02d}:00",
		}
	return schedule


def weighted_peak_order_datetime(start: datetime, end: datetime) -> datetime:
	if end <= start:
		return start

	while True:
		total_seconds = int((end - start).total_seconds())
		candidate = start + timedelta(seconds=random.randint(0, max(total_seconds, 1)))

		hour = candidate.hour
		is_weekend = candidate.weekday() >= 5

		weight = 1.0
		if is_weekend:
			weight *= 1.4
		if 12 <= hour <= 14:
			weight *= 2.2
		elif 19 <= hour <= 21:
			weight *= 2.0
		elif 11 <= hour <= 22:
			weight *= 1.3

		acceptance = min(weight / 2.4, 1.0)
		if random.random() <= acceptance:
			return candidate


def with_retries(operation_name: str, func, *args, **kwargs):
	for attempt in range(1, MAX_RETRIES + 1):
		try:
			return func(*args, **kwargs)
		except (AutoReconnect, ServerSelectionTimeoutError, BulkWriteError, PyMongoError) as exc:
			logging.warning(
				"%s falló (intento %d/%d): %s",
				operation_name,
				attempt,
				MAX_RETRIES,
				exc,
			)
			if attempt == MAX_RETRIES:
				raise
			time.sleep(RETRY_DELAY_SECONDS * attempt)


def chunked(seq: Sequence, size: int):
	for i in range(0, len(seq), size):
		yield seq[i:i + size]


def progress_log(generated: int, total: int, phase_start: float, last_ten_k: int) -> int:
	logging.info("Generando %d de %d documentos...", generated, total)
	current_block = generated // 10000
	if current_block > last_ten_k and generated > 0:
		elapsed = time.time() - phase_start
		logging.info("Tiempo parcial (%d documentos): %.2f segundos", current_block * 10000, elapsed)
		return current_block
	return last_ten_k


def insert_in_batches(collection: Collection, docs: List[Dict], batch_size: int, label: str) -> int:
	inserted = 0
	total = len(docs)
	phase_start = time.time()
	last_ten_k = 0

	for batch in chunked(docs, batch_size):
		with_retries(f"insert_many {label}", collection.insert_many, batch, ordered=False)
		inserted += len(batch)
		last_ten_k = progress_log(inserted, total, phase_start, last_ten_k)

	return inserted


def create_indexes(db: Database) -> None:
	logging.info("Creando índices...")

	with_retries(
		"index restaurantes geo",
		db.restaurantes.create_index,
		[("ubicacion", GEOSPHERE)],
		name="idx_restaurantes_ubicacion_geo",
	)
	with_retries(
		"index restaurantes text",
		db.restaurantes.create_index,
		[("nombre", TEXT), ("descripcion", TEXT), ("tipo_comida", TEXT)],
		name="idx_restaurantes_texto",
	)

	with_retries(
		"index usuarios email unique",
		db.usuarios.create_index,
		[("email", ASCENDING)],
		unique=True,
		name="idx_usuarios_email_unique",
	)
	with_retries(
		"index usuarios tipo_puntos",
		db.usuarios.create_index,
		[("tipo", ASCENDING), ("puntos", ASCENDING)],
		name="idx_usuarios_tipo_puntos",
	)

	with_retries(
		"index articulos restaurante_categoria",
		db.articulos_menu.create_index,
		[("restaurante_id", ASCENDING), ("categoria", ASCENDING)],
		name="idx_articulos_restaurante_categoria",
	)

	with_retries(
		"index ordenes usuario_fecha",
		db.ordenes.create_index,
		[("usuario_id", ASCENDING), ("fecha_pedido", ASCENDING)],
		name="idx_ordenes_usuario_fecha",
	)
	with_retries(
		"index ordenes restaurante_estado",
		db.ordenes.create_index,
		[("restaurante_id", ASCENDING), ("estado", ASCENDING)],
		name="idx_ordenes_restaurante_estado",
	)

	with_retries(
		"index resenas restaurante_calificacion",
		db.resenas.create_index,
		[("restaurante_id", ASCENDING), ("calificacion_general", ASCENDING)],
		name="idx_resenas_restaurante_calificacion",
	)
	with_retries(
		"index resenas text",
		db.resenas.create_index,
		[("titulo", TEXT), ("comentario", TEXT)],
		name="idx_resenas_texto",
	)


def clear_existing_data(db: Database) -> None:
	logging.info("Borrando datos existentes...")
	for name in ["restaurantes", "usuarios", "articulos_menu", "ordenes", "resenas"]:
		with_retries(f"drop {name}", db[name].drop)
	logging.info("Colecciones eliminadas correctamente.")


def generate_restaurantes(fake: Faker, total: int) -> Tuple[List[Dict], List[RestauranteRef]]:
	docs = []
	refs = []
	prefijos = ["Casa", "Sabor", "Rincón", "Bistro", "Fogón", "Delicia", "La", "El", "Doña", "Don"]
	sufijos = ["Chapín", "Antiguo", "del Lago", "Urbano", "Real", "del Chef", "Gourmet", "Express"]

	for _ in range(total):
		city_info = random.choice(CIUDADES_GUATEMALA)
		tipos = random.sample(TIPOS_COMIDA, random.randint(1, 3))
		oid = ObjectId()
		nombre = f"{random.choice(prefijos)} {fake.last_name()} {random.choice(sufijos)}"
		direccion = {
			"calle": fake.street_address(),
			"ciudad": city_info["ciudad"],
			"pais": "Guatemala",
			"codigo_postal": city_info["cp"],
		}

		doc = {
			"_id": oid,
			"nombre": nombre,
			"descripcion": fake.paragraph(nb_sentences=4),
			"tipo_comida": tipos,
			"direccion": direccion,
			"ubicacion": {
				"type": "Point",
				"coordinates": [
					jitter_coordinate(city_info["lon"], 0.08),
					jitter_coordinate(city_info["lat"], 0.06),
				],
			},
			"horario": generate_week_schedule(),
			"telefono": f"+502 {random.randint(2000, 7999)}-{random.randint(1000, 9999)}",
			"email": f"contacto.{oid}@rest.gt",
			"fecha_registro": random_date_within_years(5),
			"activo": random.random() < 0.90,
		}
		docs.append(doc)
		refs.append(RestauranteRef(_id=oid, nombre=nombre, direccion=direccion))

	return docs, refs


def generate_usuarios(fake: Faker, total: int) -> Tuple[List[Dict], List[UsuarioRef]]:
	docs = []
	refs = []

	for idx in range(total):
		city_info = random.choice(CIUDADES_GUATEMALA)
		oid = ObjectId()
		nombre = fake.first_name()
		apellido = fake.last_name()
		tipo = random.choices(TIPOS_USUARIO, weights=PESOS_TIPOS_USUARIO, k=1)[0]
		fecha_registro = random_date_within_years(5)
		antiguedad_dias = max((datetime.utcnow() - fecha_registro).days, 1)

		base_puntos = {
			"regular": random.randint(0, 450),
			"premium": random.randint(150, 750),
			"vip": random.randint(300, 1000),
		}[tipo]
		bono_antiguedad = min(antiguedad_dias // 20, 200)
		puntos = min(base_puntos + bono_antiguedad, 1000)

		direccion = {
			"calle": fake.street_address(),
			"ciudad": city_info["ciudad"],
			"pais": "Guatemala",
			"codigo_postal": city_info["cp"],
		}

		doc = {
			"_id": oid,
			"nombre": nombre,
			"apellido": apellido,
			"email": f"{nombre.lower()}.{apellido.lower()}.{idx}@mail.gt".replace(" ", ""),
			"telefono": f"+502 {random.randint(2000, 7999)}-{random.randint(1000, 9999)}",
			"direccion": direccion,
			"fecha_registro": fecha_registro,
			"tipo": tipo,
			"preferencias": random.sample(TIPOS_COMIDA, random.randint(2, 5)),
			"puntos": puntos,
			"activo": random.random() < 0.94,
		}

		docs.append(doc)
		refs.append(UsuarioRef(_id=oid, fecha_registro=fecha_registro, direccion=direccion, tipo=tipo))

	return docs, refs


def random_price_by_category(categoria: str) -> Decimal:
	ranges = {
		"Entrada": (Decimal("20"), Decimal("120")),
		"Plato Principal": (Decimal("45"), Decimal("350")),
		"Postre": (Decimal("25"), Decimal("140")),
		"Bebida": (Decimal("20"), Decimal("95")),
		"Acompañamiento": (Decimal("20"), Decimal("90")),
	}
	low, high = ranges[categoria]
	value = low + (high - low) * Decimal(str(random.random()))
	return quantize_money(value)


def menu_customization_options(categoria: str) -> List[Dict]:
	base = []
	if categoria in ["Plato Principal", "Entrada"]:
		base.append({"nombre": "Nivel Picante", "opciones": ["Sin picante", "Medio", "Alto"]})
	if categoria in ["Bebida"]:
		base.append({"nombre": "Tamaño", "opciones": ["Pequeño", "Mediano", "Grande"]})
		base.append({"nombre": "Hielo", "opciones": ["Sin hielo", "Normal", "Extra"]})
	if categoria in ["Postre"]:
		base.append({"nombre": "Cobertura", "opciones": ["Chocolate", "Caramelo", "Frutas"]})
	if categoria == "Plato Principal":
		base.append({"nombre": "Término", "opciones": ["3/4", "Bien cocido", "Término medio"]})
	if random.random() < 0.25:
		base.append({"nombre": "Extra", "opciones": ["Queso", "Tocino", "Salsa especial"]})
	return base


def generate_articulos_menu(
	fake: Faker,
	total: int,
	restaurantes: List[RestauranteRef],
) -> Tuple[List[Dict], List[ArticuloRef], Dict[ObjectId, List[ArticuloRef]]]:
	if not restaurantes:
		raise ValueError("No hay restaurantes para asociar artículos del menú.")

	docs = []
	refs = []
	by_restaurante: Dict[ObjectId, List[ArticuloRef]] = {r._id: [] for r in restaurantes}

	base_por_restaurante = total // len(restaurantes)
	residuo = total % len(restaurantes)

	nombres_por_categoria = {
		"Entrada": ["Nachos", "Bruschetta", "Ensalada Fresca", "Sopa del Día", "Tostadas"],
		"Plato Principal": ["Pollo Asado", "Pasta Alfredo", "Hamburguesa Especial", "Filete", "Lasaña"],
		"Postre": ["Cheesecake", "Flan", "Brownie", "Pastel de Chocolate", "Helado Artesanal"],
		"Bebida": ["Limonada", "Café", "Té Frío", "Smoothie", "Gaseosa"],
		"Acompañamiento": ["Papas Fritas", "Arroz", "Vegetales", "Pan de Ajo", "Ensalada Verde"],
	}

	for idx, restaurante in enumerate(restaurantes):
		cantidad = base_por_restaurante + (1 if idx < residuo else 0)
		for _ in range(cantidad):
			categoria = random.choice(CATEGORIAS_MENU)
			nombre = f"{random.choice(nombres_por_categoria[categoria])} {random.choice(['Especial', 'de la Casa', 'Premium', 'Tradicional'])}"
			precio = random_price_by_category(categoria)
			oid = ObjectId()

			doc = {
				"_id": oid,
				"restaurante_id": restaurante._id,
				"nombre": nombre,
				"descripcion": fake.sentence(nb_words=14),
				"categoria": categoria,
				"precio": to_decimal128(precio),
				"moneda": "GTQ",
				"disponible": random.random() < 0.92,
				"ingredientes": random.sample(INGREDIENTES_BASE, random.randint(4, 9)),
				"opciones_personalizacion": menu_customization_options(categoria),
				"imagen_url": f"https://img.restaurant.gt/menu/{oid}.jpg" if random.random() < 0.75 else None,
				"calorias": random.randint(80, 1200) if random.random() < 0.85 else None,
				"tiempo_preparacion": random.randint(5, 45),
			}

			ref = ArticuloRef(
				_id=oid,
				restaurante_id=restaurante._id,
				nombre=nombre,
				precio=precio,
				categoria=categoria,
			)

			docs.append(doc)
			refs.append(ref)
			by_restaurante[restaurante._id].append(ref)

	return docs, refs, by_restaurante


def create_delivery_address(user: UsuarioRef, fake: Faker) -> Dict:
	if random.random() < 0.75:
		return user.direccion
	city = random.choice(CIUDADES_GUATEMALA)
	return {
		"calle": fake.street_address(),
		"ciudad": city["ciudad"],
		"pais": "Guatemala",
		"codigo_postal": city["cp"],
	}


def generate_order_items(articulos_restaurante: List[ArticuloRef]) -> Tuple[List[Dict], Decimal, List[ObjectId]]:
	if not articulos_restaurante:
		raise ValueError("Restaurante sin artículos para generar orden.")

	max_items = min(5, len(articulos_restaurante))
	quantity_items = random.randint(1, max_items)
	chosen = random.sample(articulos_restaurante, quantity_items)

	items = []
	subtotal = Decimal("0")
	articulo_ids = []

	for articulo in chosen:
		cantidad = random.randint(1, 5)
		precio_unitario = articulo.precio
		item_subtotal = quantize_money(precio_unitario * Decimal(cantidad))
		subtotal += item_subtotal
		articulo_ids.append(articulo._id)

		items.append(
			{
				"articulo_id": articulo._id,
				"nombre": articulo.nombre,
				"cantidad": cantidad,
				"precio_unitario": to_decimal128(precio_unitario),
				"subtotal": to_decimal128(item_subtotal),
				"personalizaciones": random.sample(
					PERSONALIZACIONES_COMUNES,
					random.randint(0, min(2, len(PERSONALIZACIONES_COMUNES))),
				),
			}
		)

	return items, quantize_money(subtotal), articulo_ids


def validate_references_before_generation(
	usuarios: List[UsuarioRef],
	restaurantes: List[RestauranteRef],
	articulos_por_restaurante: Dict[ObjectId, List[ArticuloRef]],
) -> None:
	if not usuarios:
		raise ValueError("No existen usuarios para generar órdenes/reseñas.")
	if not restaurantes:
		raise ValueError("No existen restaurantes para generar órdenes/reseñas.")
	if not articulos_por_restaurante:
		raise ValueError("No existen artículos para generar órdenes.")
	for restaurante in restaurantes:
		if restaurante._id not in articulos_por_restaurante or not articulos_por_restaurante[restaurante._id]:
			raise ValueError(f"Integridad referencial inválida: restaurante {restaurante._id} sin artículos.")


def generate_ordenes(
	fake: Faker,
	total: int,
	usuarios: List[UsuarioRef],
	restaurantes: List[RestauranteRef],
	articulos_por_restaurante: Dict[ObjectId, List[ArticuloRef]],
) -> Tuple[List[Dict], List[OrdenRef]]:
	validate_references_before_generation(usuarios, restaurantes, articulos_por_restaurante)

	docs = []
	refs = []
	now = datetime.utcnow()
	two_years_ago = now - timedelta(days=365 * 2)

	for _ in range(total):
		usuario = random.choice(usuarios)
		restaurante = random.choice(restaurantes)
		articulos_rest = articulos_por_restaurante[restaurante._id]

		fecha_min = max(usuario.fecha_registro, two_years_ago)
		fecha_pedido = weighted_peak_order_datetime(fecha_min, now)
		estado = random.choices(ESTADOS_ORDEN, weights=PESOS_ESTADOS_ORDEN, k=1)[0]

		items, subtotal, articulo_ids = generate_order_items(articulos_rest)
		impuesto = quantize_money(subtotal * Decimal("0.12"))
		total_orden = quantize_money(subtotal + impuesto)

		oid = ObjectId()
		doc = {
			"_id": oid,
			"usuario_id": usuario._id,
			"restaurante_id": restaurante._id,
			"fecha_pedido": fecha_pedido,
			"items": items,
			"subtotal": to_decimal128(subtotal),
			"impuesto": to_decimal128(impuesto),
			"total": to_decimal128(total_orden),
			"estado": estado,
			"metodo_pago": random.choice(METODOS_PAGO),
			"direccion_entrega": create_delivery_address(usuario, fake),
			"calificacion_entrega": (
				random.randint(1, 5)
				if estado == "entregado" and random.random() < 0.70
				else None
			),
		}

		docs.append(doc)
		refs.append(
			OrdenRef(
				_id=oid,
				usuario_id=usuario._id,
				restaurante_id=restaurante._id,
				fecha_pedido=fecha_pedido,
				articulo_ids=articulo_ids,
			)
		)

	return docs, refs


def order_lookup_by_restaurant(ordenes: List[OrdenRef]) -> Dict[ObjectId, List[OrdenRef]]:
	lookup: Dict[ObjectId, List[OrdenRef]] = {}
	for orden in ordenes:
		lookup.setdefault(orden.restaurante_id, []).append(orden)
	return lookup


def generate_review_text(fake: Faker, rating: int) -> Tuple[str, str]:
	positive_titles = [
		"Excelente experiencia", "Muy recomendado", "Servicio impecable", "Comida deliciosa", "Volveré pronto"
	]
	neutral_titles = ["Buena opción", "Aceptable", "Experiencia regular", "Podría mejorar", "Cumple"]
	negative_titles = ["No cumplió expectativas", "Servicio lento", "No lo recomiendo", "Mala experiencia", "Decepcionante"]

	if rating >= 4:
		title = random.choice(positive_titles)
	elif rating == 3:
		title = random.choice(neutral_titles)
	else:
		title = random.choice(negative_titles)

	text = " ".join(fake.paragraphs(nb=random.randint(2, 4)))
	return title, text


def generate_resenas(
	fake: Faker,
	total: int,
	usuarios: List[UsuarioRef],
	restaurantes: List[RestauranteRef],
	ordenes: List[OrdenRef],
	articulos_por_restaurante: Dict[ObjectId, List[ArticuloRef]],
) -> List[Dict]:
	if not usuarios or not restaurantes:
		raise ValueError("No hay usuarios/restaurantes para generar reseñas.")

	docs = []
	now = datetime.utcnow()
	two_years_ago = now - timedelta(days=365 * 2)

	usuarios_lookup = {u._id: u for u in usuarios}
	ordenes_por_rest = order_lookup_by_restaurant(ordenes)

	for _ in range(total):
		restaurante = random.choice(restaurantes)
		usuario = random.choice(usuarios)
		calificacion = random.choices(CALIFICACIONES, weights=PESOS_CALIFICACIONES, k=1)[0]
		titulo, comentario = generate_review_text(fake, calificacion)
		oid = ObjectId()

		orden_relacionada: Optional[OrdenRef] = None
		if random.random() < 0.55 and ordenes_por_rest.get(restaurante._id):
			candidates = ordenes_por_rest[restaurante._id]
			valid_candidates = [
				o for o in candidates
				if o.usuario_id == usuario._id and o.fecha_pedido >= max(two_years_ago, usuario.fecha_registro)
			]
			if valid_candidates:
				orden_relacionada = random.choice(valid_candidates)

		if orden_relacionada:
			fecha_min = orden_relacionada.fecha_pedido + timedelta(minutes=30)
			fecha = weighted_peak_order_datetime(fecha_min, now)
		else:
			fecha_min = max(two_years_ago, usuarios_lookup[usuario._id].fecha_registro)
			fecha = weighted_peak_order_datetime(fecha_min, now)

		respuesta_restaurante = None
		if random.random() < 0.30:
			fecha_resp = fecha + timedelta(hours=random.randint(2, 96))
			if fecha_resp > now:
				fecha_resp = now
			respuesta_restaurante = {
				"fecha_respuesta": fecha_resp,
				"comentario_respuesta": fake.sentence(nb_words=16),
			}

		items_resenados = []
		if random.random() < 0.40:
			if orden_relacionada and orden_relacionada.articulo_ids:
				art_ids = random.sample(
					orden_relacionada.articulo_ids,
					k=min(len(orden_relacionada.articulo_ids), random.randint(1, 2)),
				)
				items_resenados = [
					{
						"articulo_id": art_id,
						"calificacion": random.choices(CALIFICACIONES, weights=PESOS_CALIFICACIONES, k=1)[0],
						"comentario": fake.sentence(nb_words=12),
					}
					for art_id in art_ids
				]
			else:
				articulos = articulos_por_restaurante[restaurante._id]
				picks = random.sample(articulos, k=min(len(articulos), random.randint(1, 2)))
				items_resenados = [
					{
						"articulo_id": art._id,
						"calificacion": random.choices(CALIFICACIONES, weights=PESOS_CALIFICACIONES, k=1)[0],
						"comentario": fake.sentence(nb_words=12),
					}
					for art in picks
				]

		doc = {
			"_id": oid,
			"usuario_id": usuario._id,
			"restaurante_id": restaurante._id,
			"orden_id": orden_relacionada._id if orden_relacionada else None,
			"fecha": fecha,
			"calificacion_general": calificacion,
			"titulo": titulo,
			"comentario": comentario,
			"fotos": [f"https://img.restaurant.gt/reviews/{oid}_{i}.jpg" for i in range(random.randint(1, 3))] if random.random() < 0.22 else [],
			"likes": random.randint(0, 100),
			"respuesta_restaurante": respuesta_restaurante,
			"items_resenados": items_resenados,
		}
		docs.append(doc)

	return docs


def collect_counts(db: Database) -> Dict[str, int]:
	return {
		"restaurantes": db.restaurantes.count_documents({}),
		"usuarios": db.usuarios.count_documents({}),
		"articulos_menu": db.articulos_menu.count_documents({}),
		"ordenes": db.ordenes.count_documents({}),
		"resenas": db.resenas.count_documents({}),
	}


def save_stats(path: str, stats: Dict) -> None:
	with open(path, "w", encoding="utf-8") as f:
		json.dump(stats, f, ensure_ascii=False, indent=2, default=str)


def verify_minimum_50k(counts: Dict[str, int]) -> bool:
	return any(value >= 50000 for value in counts.values())


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Generador de datos para sistema de restaurantes en MongoDB")
	parser.add_argument("--drop-existing", action="store_true", help="Borra colecciones existentes antes de generar")
	parser.add_argument("--db-name", default=os.getenv("MONGO_DB_NAME", DEFAULT_DB_NAME), help="Nombre de base de datos")
	parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="Tamaño de lote para inserciones")
	parser.add_argument("--stats-file", default=DEFAULT_STATS_FILE, help="Ruta del JSON de estadísticas")
	parser.add_argument("--seed", type=int, default=RANDOM_SEED, help="Semilla para generación reproducible")
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	configure_logging()

	random.seed(args.seed)
	fake = Faker("es_ES")
	Faker.seed(args.seed)

	mongo_uri = os.getenv("MONGO_URI")
	if not mongo_uri:
		raise ValueError("La variable de entorno MONGO_URI es obligatoria.")

	start_time = time.time()
	stats = {
		"configuracion": {
			"db_name": args.db_name,
			"batch_size": args.batch_size,
			"seed": args.seed,
			"drop_existing": args.drop_existing,
			"objetivos": COLLECTIONS,
		},
		"fases": {},
		"conteos_finales": {},
	}

	logging.info("Conectando a MongoDB Atlas...")
	client = MongoClient(mongo_uri, serverSelectionTimeoutMS=20000)
	with_retries("ping", client.admin.command, "ping")
	db = client[args.db_name]
	logging.info("Conexión exitosa. Base de datos: %s", args.db_name)

	if args.drop_existing:
		clear_existing_data(db)

	# 1) Restaurantes
	phase_start = time.time()
	restaurantes_docs, restaurantes_ref = generate_restaurantes(fake, COLLECTIONS["restaurantes"])
	inserted = insert_in_batches(db.restaurantes, restaurantes_docs, args.batch_size, "restaurantes")
	stats["fases"]["restaurantes"] = {"insertados": inserted, "tiempo_segundos": round(time.time() - phase_start, 2)}

	# 2) Usuarios
	phase_start = time.time()
	usuarios_docs, usuarios_ref = generate_usuarios(fake, COLLECTIONS["usuarios"])
	inserted = insert_in_batches(db.usuarios, usuarios_docs, args.batch_size, "usuarios")
	stats["fases"]["usuarios"] = {"insertados": inserted, "tiempo_segundos": round(time.time() - phase_start, 2)}

	# 3) Artículos del menú
	phase_start = time.time()
	articulos_docs, articulos_ref, articulos_por_restaurante = generate_articulos_menu(
		fake,
		COLLECTIONS["articulos_menu"],
		restaurantes_ref,
	)
	inserted = insert_in_batches(db.articulos_menu, articulos_docs, args.batch_size, "articulos_menu")
	stats["fases"]["articulos_menu"] = {"insertados": inserted, "tiempo_segundos": round(time.time() - phase_start, 2)}

	# 4) Órdenes
	phase_start = time.time()
	ordenes_docs, ordenes_ref = generate_ordenes(
		fake,
		COLLECTIONS["ordenes"],
		usuarios_ref,
		restaurantes_ref,
		articulos_por_restaurante,
	)
	inserted = insert_in_batches(db.ordenes, ordenes_docs, args.batch_size, "ordenes")
	stats["fases"]["ordenes"] = {"insertados": inserted, "tiempo_segundos": round(time.time() - phase_start, 2)}

	# 5) Reseñas
	phase_start = time.time()
	resenas_docs = generate_resenas(
		fake,
		COLLECTIONS["resenas"],
		usuarios_ref,
		restaurantes_ref,
		ordenes_ref,
		articulos_por_restaurante,
	)
	inserted = insert_in_batches(db.resenas, resenas_docs, args.batch_size, "resenas")
	stats["fases"]["resenas"] = {"insertados": inserted, "tiempo_segundos": round(time.time() - phase_start, 2)}

	# Índices
	phase_start = time.time()
	create_indexes(db)
	stats["fases"]["indices"] = {"tiempo_segundos": round(time.time() - phase_start, 2)}

	# Conteos y validación final
	counts = collect_counts(db)
	stats["conteos_finales"] = counts
	stats["validacion_min_50000"] = verify_minimum_50k(counts)
	stats["tiempo_total_segundos"] = round(time.time() - start_time, 2)
	stats["fecha_ejecucion"] = datetime.utcnow().isoformat() + "Z"

	save_stats(args.stats_file, stats)

	logging.info("=" * 70)
	logging.info("Estadísticas finales")
	logging.info("Restaurantes: %d", counts["restaurantes"])
	logging.info("Usuarios: %d", counts["usuarios"])
	logging.info("Artículos menú: %d", counts["articulos_menu"])
	logging.info("Órdenes: %d", counts["ordenes"])
	logging.info("Reseñas: %d", counts["resenas"])
	logging.info("Cumple mínimo 50,000 en al menos una colección: %s", "Sí" if stats["validacion_min_50000"] else "No")
	logging.info("Tiempo total: %.2f segundos", stats["tiempo_total_segundos"])
	logging.info("Estadísticas guardadas en: %s", args.stats_file)


if __name__ == "__main__":
	try:
		main()
	except Exception as exc:
		logging.exception("Error durante la generación de datos: %s", exc)
		raise
