export const restaurants = [
  {
    id: 1,
    name: "Vista al Lago",
    category: "Italiana",
    rating: 4.8,
    image:
      "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=800&q=80",
    description:
      "Restaurante con ambiente elegante y vista privilegiada, especializado en pastas y platillos italianos.",
    location: "Zona 10, Ciudad de Guatemala",
    hours: "10:00 AM - 10:00 PM",
    menu: [
      {
        id: 101,
        name: "Pasta Carbonara",
        description: "Pasta cremosa con tocino, queso parmesano y pimienta negra.",
        price: 78,
        image:
          "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?auto=format&fit=crop&w=800&q=80",
      },
      {
        id: 102,
        name: "Lasaña Clásica",
        description: "Capas de pasta con salsa boloñesa y queso gratinado.",
        price: 85,
        image:
          "https://images.unsplash.com/photo-1619895092538-128341789043?auto=format&fit=crop&w=800&q=80",
      },
    ],
  },
  {
    id: 2,
    name: "El Rinconcito",
    category: "Guatemalteca",
    rating: 4.7,
    image:
      "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",
    description:
      "Comida tradicional guatemalteca con sazón casera y ambiente familiar.",
    location: "Antigua Guatemala",
    hours: "8:00 AM - 9:00 PM",
    menu: [
      {
        id: 201,
        name: "Pepián",
        description: "Platillo tradicional con pollo, verduras y recado espeso.",
        price: 65,
        image:
          "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=800&q=80",
      },
      {
        id: 202,
        name: "Jocón",
        description: "Pollo en salsa verde acompañado de arroz.",
        price: 62,
        image:
          "https://images.unsplash.com/photo-1516684669134-de6f7c473a2a?auto=format&fit=crop&w=800&q=80",
      },
    ],
  },
  {
    id: 3,
    name: "Café Colonial",
    category: "Café",
    rating: 4.6,
    image:
      "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=80",
    description:
      "Café acogedor con bebidas artesanales, postres y desayunos ligeros.",
    location: "Zona 1, Ciudad de Guatemala",
    hours: "7:00 AM - 8:00 PM",
    menu: [
      {
        id: 301,
        name: "Cappuccino",
        description: "Espresso con leche vaporizada y espuma cremosa.",
        price: 28,
        image:
          "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=800&q=80",
      },
      {
        id: 302,
        name: "Cheesecake",
        description: "Postre cremoso con base de galleta y topping de frutos rojos.",
        price: 32,
        image:
          "https://images.unsplash.com/photo-1567171466295-4afa63d45416?auto=format&fit=crop&w=800&q=80",
      },
    ],
  },
  {
    id: 4,
    name: "Parrilla 502",
    category: "Parrilla",
    rating: 4.7,
    image:
      "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=800&q=80",
    description:
      "Especialistas en cortes de carne, parrilladas y acompañamientos artesanales.",
    location: "Carretera a El Salvador",
    hours: "12:00 PM - 11:00 PM",
    menu: [
      {
        id: 401,
        name: "Costillas BBQ",
        description: "Costillas bañadas en salsa BBQ con papas rústicas.",
        price: 95,
        image:
          "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?auto=format&fit=crop&w=800&q=80",
      },
      {
        id: 402,
        name: "Steak Premium",
        description: "Corte jugoso acompañado de vegetales y puré.",
        price: 120,
        image:
          "https://images.unsplash.com/photo-1600891964092-4316c288032e?auto=format&fit=crop&w=800&q=80",
      },
    ],
  },
];

export const categories = [
  {
    id: 1,
    name: "Italiana",
    rating: 4.8,
    image:
      "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 2,
    name: "Guatemalteca",
    rating: 4.7,
    image:
      "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 3,
    name: "Café",
    rating: 4.6,
    image:
      "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 4,
    name: "Parrilla",
    rating: 4.7,
    image:
      "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?auto=format&fit=crop&w=800&q=80",
  },
];

export const reviews = [
  {
    id: 1,
    user: "Carlos Hernández",
    restaurant: "Vista al Lago",
    restaurantId: 1,
    comment: "Increíble vista y la pasta carbonara es deliciosa, volveré.",
    rating: 4.8,
  },
  {
    id: 2,
    user: "Ana López",
    restaurant: "El Rinconcito",
    restaurantId: 2,
    comment: "El pepián estaba riquísimo, pero el servicio fue un poco lento.",
    rating: 4.6,
  },
  {
    id: 3,
    user: "Daniel Martínez",
    restaurant: "Parrilla 502",
    restaurantId: 4,
    comment: "La carne en su punto, ambiente acogedor y buen servicio.",
    rating: 4.7,
  },
  {
    id: 4,
    user: "Angel Squit",
    restaurant: "Café Colonial",
    restaurantId: 3,
    comment: "El café estaba excelente y el lugar es muy bonito.",
    rating: 4.5,
  },
];

export const orders = [
  {
    id: 1,
    restaurantId: 1,
    restaurant: "Vista al Lago",
    status: "Entregada",
    total: 156,
    date: "08/03/2026",
    customer: "Mia Fuentes",
    items: [
      { name: "Pasta Carbonara", quantity: 1, price: 78 },
      { name: "Lasaña Clásica", quantity: 1, price: 78 },
    ],
  },
  {
    id: 2,
    restaurantId: 4,
    restaurant: "Parrilla 502",
    status: "En proceso",
    total: 95,
    date: "07/03/2026",
    customer: "Anggelie Velásquez",
    items: [{ name: "Costillas BBQ", quantity: 1, price: 95 }],
  },
  {
    id: 3,
    restaurantId: 3,
    restaurant: "Café Colonial",
    status: "Pendiente",
    total: 60,
    date: "06/03/2026",
    customer: "Anggelie Velásquez",
    items: [
      { name: "Cappuccino", quantity: 1, price: 28 },
      { name: "Cheesecake", quantity: 1, price: 32 },
    ],
  },
];