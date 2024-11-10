import React from 'react';
import { useProductContext } from '../context/ProductContext';
import { Edit2, Trash2 } from 'lucide-react';

export const ProductListings: React.FC = () => {
  const { products, removeProduct } = useProductContext();

  if (products.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-lg shadow-sm">
        <p className="text-gray-500">No products imported yet. Add your first product above!</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Your Products</h2>
      <div className="grid gap-6 md:grid-cols-2">
        {products.map((product) => (
          <div
            key={product.id}
            className="bg-white rounded-lg shadow-sm overflow-hidden"
          >
            <div className="aspect-video relative">
              <img
                src={product.image}
                alt={product.title}
                className="w-full h-full object-cover"
              />
              <div className="absolute top-2 right-2 flex space-x-2">
                <button
                  onClick={() => removeProduct(product.id)}
                  className="p-2 bg-white rounded-full shadow-md hover:bg-red-50 transition-colors"
                >
                  <Trash2 className="w-4 h-4 text-red-500" />
                </button>
                <button className="p-2 bg-white rounded-full shadow-md hover:bg-blue-50 transition-colors">
                  <Edit2 className="w-4 h-4 text-blue-500" />
                </button>
              </div>
            </div>
            <div className="p-4">
              <h3 className="font-semibold text-lg mb-2">{product.title}</h3>
              <p className="text-gray-600 text-sm mb-3">{product.description}</p>
              <div className="flex items-center justify-between">
                <span className="font-bold text-lg">${product.price}</span>
                <span className="text-sm text-gray-500">
                  From {product.source}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};