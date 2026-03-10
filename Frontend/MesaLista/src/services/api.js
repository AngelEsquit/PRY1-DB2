const API_URL = "http://127.0.0.1:8000";

export async function fetchRestaurants() {
  const res = await fetch(`${API_URL}/restaurants`);
  if (!res.ok) throw new Error("Error al obtener restaurantes");
  return res.json();
}

export async function fetchRestaurantDetail(id) {
  const res = await fetch(`${API_URL}/restaurants/${id}`);
  if (!res.ok) throw new Error("Error al obtener detalle del restaurante");
  return res.json();
}

export async function fetchOrders() {
  const res = await fetch(`${API_URL}/orders`);
  if (!res.ok) throw new Error("Error al obtener órdenes");
  return res.json();
}

export async function fetchReviews() {
  const res = await fetch(`${API_URL}/reviews`);
  if (!res.ok) throw new Error("Error al obtener reseñas");
  return res.json();
}

export async function createReview(data) {
  const res = await fetch(`${API_URL}/reviews`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!res.ok) throw new Error("Error al crear reseña");
  return res.json();
}

export async function createOrder(data) {
  const res = await fetch(`${API_URL}/orders`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!res.ok) throw new Error("Error al crear orden");
  return res.json();
}