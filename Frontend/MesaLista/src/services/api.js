const API_URL = "http://127.0.0.1:8000";

async function handleResponse(res, defaultMessage) {
  if (!res.ok) {
    let detail = defaultMessage;
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch {
      // ignore
    }
    throw new Error(detail);
  }
  return res.json();
}

export async function fetchRestaurants() {
  const res = await fetch(`${API_URL}/restaurants/`);
  return handleResponse(res, "Error al obtener restaurantes");
}

export async function fetchRestaurantDetail(id) {
  const res = await fetch(`${API_URL}/restaurants/${id}`);
  return handleResponse(res, "Error al obtener detalle del restaurante");
}

export async function fetchOrders() {
  const res = await fetch(`${API_URL}/orders/`);
  return handleResponse(res, "Error al obtener órdenes");
}

export async function fetchOrderDetail(id) {
  const res = await fetch(`${API_URL}/orders/${id}`);
  return handleResponse(res, "Error al obtener detalle de la orden");
}

export async function fetchReviews() {
  const res = await fetch(`${API_URL}/reviews/`);
  return handleResponse(res, "Error al obtener reseñas");
}

export async function createReview(data) {
  const res = await fetch(`${API_URL}/reviews/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return handleResponse(res, "Error al crear reseña");
}

export async function createOrder(data) {
  const res = await fetch(`${API_URL}/orders/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return handleResponse(res, "Error al crear orden");
}

export async function fetchTopDishesReport({ year, month, restaurantId, limit = 10 }) {
  const params = new URLSearchParams({
    year: String(year),
    month: String(month),
    limit: String(limit),
  });

  if (restaurantId) {
    params.set("restaurant_id", restaurantId);
  }

  const res = await fetch(`${API_URL}/reports/top-dishes?${params.toString()}`);
  return handleResponse(res, "Error al obtener reporte de platillos");
}

export async function fetchTopRatedRestaurantsReport({ minReviews = 5, limit = 10 }) {
  const params = new URLSearchParams({
    min_reviews: String(minReviews),
    limit: String(limit),
  });

  const res = await fetch(
    `${API_URL}/reports/top-rated-restaurants?${params.toString()}`
  );
  return handleResponse(res, "Error al obtener reporte de restaurantes");
}

export async function fetchPeakHoursReport(restaurantId) {
  const params = new URLSearchParams({ restaurant_id: restaurantId });
  const res = await fetch(`${API_URL}/reports/peak-hours?${params.toString()}`);
  return handleResponse(res, "Error al obtener reporte de horas pico");
}

// ── CRUD: Users ──────────────────────────────────────────────────

export async function fetchUsers(tipo) {
  const res = await fetch(`${API_URL}/users/`);
  return handleResponse(res, "Error al obtener usuarios");
}

export async function fetchUserDetail(id) {
  const res = await fetch(`${API_URL}/users/${id}`);
  return handleResponse(res, "Error al obtener usuario");
}

export async function createUser(data) {
  const res = await fetch(`${API_URL}/users/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse(res, "Error al crear usuario");
}

export async function updateUserEmail(id, nuevo_email) {
  const res = await fetch(`${API_URL}/users/${id}/email`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nuevo_email }),
  });
  return handleResponse(res, "Error al actualizar email");
}

export async function deleteUser(id) {
  const res = await fetch(`${API_URL}/users/${id}`, { method: "DELETE" });
  return handleResponse(res, "Error al eliminar usuario");
}

// ── CRUD: Restaurants ────────────────────────────────────────────

export async function createRestaurant(data) {
  const res = await fetch(`${API_URL}/restaurants/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse(res, "Error al crear restaurante");
}

export async function updateRestaurantPhone(id, nuevo_telefono) {
  const res = await fetch(`${API_URL}/restaurants/${id}/phone`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nuevo_telefono }),
  });
  return handleResponse(res, "Error al actualizar teléfono");
}

export async function deleteRestaurant(id) {
  const res = await fetch(`${API_URL}/restaurants/${id}`, { method: "DELETE" });
  return handleResponse(res, "Error al eliminar restaurante");
}

export async function createMenuItem(restaurantId, data) {
  const res = await fetch(`${API_URL}/restaurants/${restaurantId}/menu`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse(res, "Error al crear artículo de menú");
}

export async function updateMenuItemPrice(itemId, nuevo_precio) {
  const res = await fetch(`${API_URL}/restaurants/items/${itemId}/price`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nuevo_precio }),
  });
  return handleResponse(res, "Error al actualizar precio");
}

export async function deleteMenuItem(itemId) {
  const res = await fetch(`${API_URL}/restaurants/items/${itemId}`, { method: "DELETE" });
  return handleResponse(res, "Error al eliminar artículo");
}

// ── CRUD: Reviews & Orders ───────────────────────────────────────

export async function deleteReview(id) {
  const res = await fetch(`${API_URL}/reviews/${id}`, { method: "DELETE" });
  return handleResponse(res, "Error al eliminar reseña");
}

export async function updateOrderStatus(id, nuevo_estado) {
  const res = await fetch(`${API_URL}/orders/${id}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nuevo_estado }),
  });
  return handleResponse(res, "Error al cambiar estado de la orden");
}

// ── Admin Bulk Operations ─────────────────────────────────────────

export async function deactivateInactiveUsers(months = 6) {
  const res = await fetch(`${API_URL}/admin/deactivate-inactive-users?months=${months}`, { method: "POST" });
  return handleResponse(res, "Error al desactivar usuarios inactivos");
}

export async function applyCategoryDiscount(categoria, porcentaje_descuento) {
  const res = await fetch(`${API_URL}/admin/apply-category-discount`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ categoria, porcentaje_descuento }),
  });
  return handleResponse(res, "Error al aplicar descuento");
}

export async function markOldOrders() {
  const res = await fetch(`${API_URL}/admin/mark-old-orders`, { method: "POST" });
  return handleResponse(res, "Error al marcar órdenes anticuadas");
}

export async function cleanOldReviews(years = 2) {
  const res = await fetch(`${API_URL}/admin/old-reviews?years=${years}`, { method: "DELETE" });
  return handleResponse(res, "Error al limpiar reseñas antiguas");
}

export async function cleanInactiveUsers() {
  const res = await fetch(`${API_URL}/admin/inactive-users`, { method: "DELETE" });
  return handleResponse(res, "Error al limpiar usuarios inactivos");
}

export async function cleanCancelledOrders() {
  const res = await fetch(`${API_URL}/admin/cancelled-orders`, { method: "DELETE" });
  return handleResponse(res, "Error al limpiar órdenes canceladas");
}

// ── Arrays ────────────────────────────────────────────────────────

export async function addUserPreference(usuario_id, preferencia) {
  const res = await fetch(`${API_URL}/arrays/preferences/add`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ usuario_id, preferencia }),
  });
  return handleResponse(res, "Error al agregar preferencia");
}

export async function removeUserPreference(usuario_id, preferencia) {
  const res = await fetch(`${API_URL}/arrays/preferences/remove`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ usuario_id, preferencia }),
  });
  return handleResponse(res, "Error al eliminar preferencia");
}

export async function addRestaurantSchedule(restaurante_id, dia, apertura, cierre) {
  const res = await fetch(`${API_URL}/arrays/schedule/add`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ restaurante_id, dia, apertura, cierre }),
  });
  return handleResponse(res, "Error al agregar horario");
}

export async function addReviewReply(resena_id, texto, autor = "Restaurante") {
  const res = await fetch(`${API_URL}/arrays/reviews/reply/add`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resena_id, texto, autor }),
  });
  return handleResponse(res, "Error al agregar respuesta");
}

export async function removeReviewReply(resena_id, texto) {
  const res = await fetch(`${API_URL}/arrays/reviews/reply/remove`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resena_id, texto }),
  });
  return handleResponse(res, "Error al eliminar respuesta");
}

// ── Transactions ──────────────────────────────────────────────────

export async function deleteUserWithCascade(userId) {
  const res = await fetch(`${API_URL}/transactions/users/${userId}`, { method: "DELETE" });
  return handleResponse(res, "Error al eliminar usuario con dependencias");
}

// ── GridFS ────────────────────────────────────────────────────────

export async function listGridFSFiles() {
  const res = await fetch(`${API_URL}/gridfs/files`);
  return handleResponse(res, "Error al listar archivos");
}

export async function uploadGridFSFile(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_URL}/gridfs/files`, { method: "POST", body: form });
  return handleResponse(res, "Error al subir archivo");
}

export async function getGridFSFileInfo(fileId) {
  const res = await fetch(`${API_URL}/gridfs/files/${fileId}/info`);
  return handleResponse(res, "Error al obtener info del archivo");
}

export function getGridFSDownloadURL(fileId) {
  return `${API_URL}/gridfs/files/${fileId}/download`;
}

export async function deleteGridFSFile(fileId) {
  const res = await fetch(`${API_URL}/gridfs/files/${fileId}`, { method: "DELETE" });
  return handleResponse(res, "Error al eliminar archivo");
}

// ── Indices ───────────────────────────────────────────────────────

export async function fetchIndexComparison() {
  const res = await fetch(`${API_URL}/indices/comparison`);
  return handleResponse(res, "Error al ejecutar comparación de índices");
}

// ── Reports (extra) ───────────────────────────────────────────────

export async function fetchSalesByRestaurantReport() {
  const res = await fetch(`${API_URL}/reports/sales-by-restaurant`);
  return handleResponse(res, "Error al obtener reporte de ventas");
}

export async function fetchAvgSpendPerUserReport(limit = 10) {
  const res = await fetch(`${API_URL}/reports/avg-spend-per-user?limit=${limit}`);
  return handleResponse(res, "Error al obtener reporte de gasto promedio");
}