import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchProduct, productImageUrl } from "../api";
import type { Product } from "../types";

export default function ProductDetailPage() {
  const { productId } = useParams<{ productId: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    if (!productId) return;
    setStatus("loading");
    fetchProduct(productId)
      .then((data) => {
        setProduct(data);
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  }, [productId]);

  if (status === "loading") {
    return (
      <div className="page">
        <p className="state-message">Loading product...</p>
      </div>
    );
  }

  if (status === "error" || !product) {
    return (
      <div className="page">
        <p className="state-message">Couldn't find that product.</p>
        <Link to="/products" className="back-link">
          ← Back to all products
        </Link>
      </div>
    );
  }

  return (
    <div className="page">
      <Link to="/products" className="back-link">
        ← Back to all products
      </Link>
      <div className="product-detail">
        <div className="product-detail-image">
          <img src={productImageUrl(product.image_url)} alt={product.name} />
        </div>
        <div className="product-detail-info">
          <h1>{product.name}</h1>
          <div className="product-detail-type">{product.garment_type}</div>
          <div className="product-detail-price">${product.price.toFixed(2)}</div>
          <p className="product-detail-description">{product.description}</p>

          <div className="product-detail-colors">
            <strong>Colors</strong>
            <div className="swatch-list">
              {product.colors.map((color) => (
                <span key={color} className="swatch">
                  {color}
                </span>
              ))}
            </div>
          </div>

          <div>
            <strong>Sizes &amp; Stock</strong>
            <table className="size-table">
              <thead>
                <tr>
                  <th>Size</th>
                  <th>Availability</th>
                </tr>
              </thead>
              <tbody>
                {product.inventory.map((item) => (
                  <tr key={item.size}>
                    <td>{item.size}</td>
                    <td className={item.quantity > 0 ? "stock-in" : "stock-out"}>
                      {item.quantity > 0 ? `${item.quantity} in stock` : "Sold out"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
