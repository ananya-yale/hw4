import { useEffect, useMemo, useState } from "react";
import ProductCard from "../components/ProductCard";
import { fetchProducts } from "../api";
import { useSearchResults } from "../SearchResultsContext";
import type { Product } from "../types";

type SortOrder = "default" | "price-asc" | "price-desc";

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const { results, query, clearResults } = useSearchResults();
  const [garmentTypeFilter, setGarmentTypeFilter] = useState("all");
  const [sortOrder, setSortOrder] = useState<SortOrder>("default");

  useEffect(() => {
    fetchProducts()
      .then((data) => {
        setProducts(data);
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  }, []);

  // Reset filter/sort whenever the underlying product set changes (e.g. a new
  // chat search comes in, or the user goes back to the full catalogue) so an
  // old filter can't silently hide a brand-new result set.
  useEffect(() => {
    setGarmentTypeFilter("all");
    setSortOrder("default");
  }, [results]);

  const showingSearchResults = results !== null;
  const baseProducts = showingSearchResults ? results : products;

  const garmentTypes = useMemo(
    () => Array.from(new Set(baseProducts.map((p) => p.garment_type))).sort(),
    [baseProducts],
  );

  const displayedProducts = useMemo(() => {
    let list = baseProducts;
    if (garmentTypeFilter !== "all") {
      list = list.filter((p) => p.garment_type === garmentTypeFilter);
    }
    if (sortOrder !== "default") {
      list = [...list].sort((a, b) =>
        sortOrder === "price-asc" ? a.price - b.price : b.price - a.price,
      );
    }
    return list;
  }, [baseProducts, garmentTypeFilter, sortOrder]);

  const showToolbar = showingSearchResults ? baseProducts.length > 0 : status === "ready";

  return (
    <div className="page">
      <div className="products-header">
        {showingSearchResults ? (
          <>
            <h1>Chat Search Results</h1>
            <p>
              Showing {baseProducts.length} match{baseProducts.length === 1 ? "" : "es"} for "{query}"
            </p>
            <button className="link-button" onClick={clearResults}>
              ← View all products
            </button>
          </>
        ) : (
          <>
            <h1>Shop All Gear</h1>
            <p>Every design in the Campus Customs catalog, in one place.</p>
          </>
        )}
      </div>

      {!showingSearchResults && status === "loading" && (
        <p className="state-message">Loading products...</p>
      )}
      {!showingSearchResults && status === "error" && (
        <p className="state-message">
          Couldn't load products. Is the backend running at localhost:8000?
        </p>
      )}
      {showingSearchResults && baseProducts.length === 0 && (
        <p className="state-message">No matches found for that search.</p>
      )}

      {showToolbar && (
        <div className="products-toolbar">
          <label>
            Type
            <select value={garmentTypeFilter} onChange={(e) => setGarmentTypeFilter(e.target.value)}>
              <option value="all">All types</option>
              {garmentTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </label>
          <label>
            Sort by
            <select value={sortOrder} onChange={(e) => setSortOrder(e.target.value as SortOrder)}>
              <option value="default">Featured</option>
              <option value="price-asc">Price: Low to High</option>
              <option value="price-desc">Price: High to Low</option>
            </select>
          </label>
          {displayedProducts.length !== baseProducts.length && (
            <span className="products-toolbar-count">
              {displayedProducts.length} of {baseProducts.length} shown
            </span>
          )}
        </div>
      )}

      {showToolbar && (
        <div className="product-grid">
          {displayedProducts.map((product) => (
            <ProductCard key={product.product_id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
}
