function MenuItemCard({ item, onOpenModal }) {
  return (
    <article className="menu-card">
      <img src={item.image} alt={item.name} className="menu-image" />

      <div className="menu-body">
        <h3>{item.name}</h3>
        <p>{item.description}</p>
        <p className="menu-price">Q{item.price.toFixed(2)}</p>

        <div className="menu-actions">
          <button className="btn btn-accent" onClick={() => onOpenModal(item)}>
            Agregar
          </button>
        </div>
      </div>
    </article>
  );
}

export default MenuItemCard;