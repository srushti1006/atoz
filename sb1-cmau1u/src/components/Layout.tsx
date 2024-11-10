import React from 'react';
import { ShoppingBag } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <ShoppingBag className="w-8 h-8 text-blue-500" />
            <h1 className="text-xl font-semibold text-gray-900">Social Product Importer</h1>
          </div>
        </div>
      </header>
      <main>{children}</main>
    </div>
  );
};