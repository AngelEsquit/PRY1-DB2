function SearchBar({ value, onChange, placeholder = "Buscar restaurantes..." }) {
  return (
    <div className="container search-wrapper">
      <input
        className="search-input"
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

export default SearchBar;