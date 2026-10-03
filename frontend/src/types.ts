export interface InventoryItem {
  size: string;
  quantity: number;
}

export interface Product {
  product_id: string;
  name: string;
  garment_type: string;
  description: string;
  colors: string[];
  search_tags: string[];
  image_url: string;
  price: number;
  inventory: InventoryItem[];
  total_stock: number;
  low_stock_sizes: string[];
}

export interface User {
  id: number;
  first_name: string | null;
  last_name: string | null;
  name: string;
  email: string;
}

export interface ChatProductCard {
  product_id: string;
  name: string;
  garment_type: string;
  description: string;
  colors: string[];
  image_url: string;
  price: number;
  inventory: InventoryItem[];
  total_stock: number;
  low_stock_sizes: string[];
}

export interface ChatReply {
  reply: string;
  products: ChatProductCard[];
}

export interface ChatHistoryMessage {
  role: "user" | "assistant";
  content: string;
  products: ChatProductCard[];
  created_at: string;
}
