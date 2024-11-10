import React from 'react';
import { Layout } from './components/Layout';
import { ProductImporter } from './components/ProductImporter';
import { ProductListings } from './components/ProductListings';
import { ProductProvider } from './context/ProductContext';

function App() {
  return (
    <ProductProvider>
      <Layout>
        <div className="max-w-4xl mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Product Listing Creator</h1>
          <ProductImporter />
          <ProductListings />
        </div>
      </Layout>
    </ProductProvider>
  );
}

export default App;