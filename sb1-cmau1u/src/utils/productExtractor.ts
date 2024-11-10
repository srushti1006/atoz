import { Product } from '../types';

const SUPPORTED_DOMAINS = ['instagram.com', 'facebook.com', 'pinterest.com'];

export async function extractProductInfo(url: string): Promise<Product> {
  // Validate URL
  const urlObj = new URL(url);
  const domain = urlObj.hostname.replace('www.', '');
  
  if (!SUPPORTED_DOMAINS.some(d => domain.includes(d))) {
    throw new Error('Unsupported platform. Please use Instagram, Facebook, or Pinterest URLs.');
  }

  // For demo purposes, simulate API call with mock data
  await new Promise(resolve => setTimeout(resolve, 1500));

  // In a real application, you would:
  // 1. Call your backend API to fetch the product info
  // 2. Parse the response from the social media platform
  // 3. Extract relevant product details
  // 4. Format and return the data

  // Mock response
  return {
    id: crypto.randomUUID(),
    title: 'Sample Product',
    description: 'This is a sample product imported from social media',
    price: 99.99,
    image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e',
    source: domain.includes('instagram.com') 
      ? 'Instagram' 
      : domain.includes('facebook.com')
      ? 'Facebook'
      : 'Pinterest',
    originalUrl: url,
    createdAt: new Date(),
  };
}