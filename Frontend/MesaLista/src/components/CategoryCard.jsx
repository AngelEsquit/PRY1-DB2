function CategoryCard({ category }) {
  return (
    <article className="card">
      <img src={category.image} alt={category.name} className="card-image" />

      <div className="card-body">
        <h3>{category.name}</h3>
        <p className="rating"> {category.rating}</p>
      </div>
    </article>
  );
}

export default CategoryCard;