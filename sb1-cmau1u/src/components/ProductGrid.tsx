import React from 'react';
import { Star } from 'lucide-react';
import { Product } from '../types';

const products: Product[] = [
  {
    id: 1,
    name: "Wireless Noise-Cancelling Headphones",
    price: 299.99,
    rating: 4.5,
    image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&q=80&w=1470",
    description: "Premium wireless headphones with active noise cancellation"
  },
  {
    id: 2,
    name: "Smart Watch Series 5",
    price: 399.99,
    rating: 4.8,
    image: "https://images.unsplash.com/photo-1546868871-7041f2a55e12?auto=format&fit=crop&q=80&w=1464",
    description: "Advanced smartwatch with health monitoring features"
  },
  {
    id: 3,
    name: "4K Ultra HD Smart TV",
    price: 799.99,
    rating: 4.7,
    image: "https://images.unsplash.com/photo-1593784991095-a205069470b6?auto=format&fit=crop&q=80&w=1470",
    description: "55-inch 4K Smart TV with HDR"
  },
  {
    id: 4,
    name: "Professional Camera Kit",
    price: 1299.99,
    rating: 4.9,
    image: "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&q=80&w=1464",
    description: "Professional DSLR camera with premium lens kit"
  },
  {
    id: 5,
    name: "Gaming Laptop",
    price: 1499.99,
    rating: 4.6,
    image: "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&q=80&w=1468",
    description: "High-performance gaming laptop with RGB keyboard"
  },
  {
    id: 6,
    name: "Wireless Earbuds",
    price: 159.99,
    rating: 4.4,
    image: "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&q=80&w=1469",
    description: "True wireless earbuds with premium sound quality"
  },
];

interface ProductGridProps {
  onAddToCart: (product: Product) => void;
}

const ProductGrid: React.FC<ProductGridProps> = ({ onAddToCart }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {products.map((product) => (
        <div key={product.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
          <div className="relative h-64">
            <img
              src={product.image}
              alt={product.name}
              className="w-full h-full object-cover"
            />
          </div>
          <div className="p-6">
            <h3 className="text-xl font-semibold mb-2">{product.name}</h3>
            <p className="text-gray-600 mb-4">{product.description}</p>
            <div className="flex items-center mb-4">
              <div className="flex items-center">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`w-5 h-5 ${
                      i < Math.floor(product.rating)
                        ? 'text-yellow-400 fill-current'
                        : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
              <span className="ml-2 text-gray-600">({product.rating})</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">${product.price}</span>
              <button
                onClick={() => onAddToCart(product)}
                className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold transition-colors"
              >
                Add to Cart
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ProductGrid;