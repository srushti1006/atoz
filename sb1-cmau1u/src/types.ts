export interface Product {
  id: string;
  title: string;
  description: string;
  price: number;
  image: string;
  source: 'Instagram' | 'Facebook' | 'Pinterest';
  originalUrl: string;
  createdAt: Date;
}

export interface ProductError extends Error {
  code: 'INVALID_URL' | 'FETCH_ERROR' | 'PARSING_ERROR';
}