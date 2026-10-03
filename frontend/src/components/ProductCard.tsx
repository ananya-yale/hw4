import { Link } from "react-router-dom";
import { productImageUrl } from "../api";

// A product only gets the "Selling Fast" badge when its stock is low across
// ALL sizes combined — not just one size out of six, which (given how the
// catalogue's per-size quantities are distributed) would otherwise flag the
// majority of products and make the badge meaningless.
const SELLING_FAST_THRESHOLD = 25;

interface ProductCardData {
  product_id: string;
  name: string;
  description: string;
  price: number;
  image_url: string;
  total_stock?: number;
}

export default function ProductCard({ product }: { product: ProductCardData }) {
  const isLowStock = (product.total_stock ?? Infinity) <= SELLING_FAST_THRESHOLD;

  return (
    <Link to={`/products/${product.product_id}`} className="product-card">
      <div className="product-card-image">
        {isLowStock && <span className="low-stock-badge">Selling Fast</span>}
        <img src={productImageUrl(product.image_url)} alt={product.name} loading="lazy" />
      </div>
      <div className="product-card-body">
        <h3>{product.name}</h3>
        <p className="product-card-desc">{product.description}</p>
        <span className="product-card-price">${product.price.toFixed(2)}</span>
      </div>
    </Link>
  );
}
