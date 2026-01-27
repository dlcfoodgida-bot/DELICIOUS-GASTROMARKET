import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../services/api';

interface CartItem {
  product_id: string;
  quantity: number;
}

interface Product {
  id: string;
  name: string;
  name_tr: string;
  price: number;
  original_price?: number;
  image_url: string;
  unit: string;
}

interface CartState {
  sessionId: string;
  items: CartItem[];
  products: Product[];
  isLoading: boolean;
  initSession: () => Promise<void>;
  fetchCart: () => Promise<void>;
  addToCart: (productId: string, quantity?: number) => Promise<void>;
  updateQuantity: (productId: string, quantity: number) => Promise<void>;
  removeFromCart: (productId: string) => Promise<void>;
  clearCart: () => Promise<void>;
  getTotalItems: () => number;
  getTotalPrice: () => number;
}

export const useCartStore = create<CartState>((set, get) => ({
  sessionId: '',
  items: [],
  products: [],
  isLoading: false,

  initSession: async () => {
    try {
      let sessionId = await AsyncStorage.getItem('session_id');
      if (!sessionId) {
        sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
        await AsyncStorage.setItem('session_id', sessionId);
      }
      set({ sessionId });
      await get().fetchCart();
    } catch (error) {
      console.error('Error initializing session:', error);
    }
  },

  fetchCart: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    
    set({ isLoading: true });
    try {
      const response = await api.get(`/cart/${sessionId}`);
      set({ 
        items: response.data.items || [], 
        products: response.data.products || [],
        isLoading: false 
      });
    } catch (error) {
      console.error('Error fetching cart:', error);
      set({ isLoading: false });
    }
  },

  addToCart: async (productId: string, quantity: number = 1) => {
    const { sessionId } = get();
    if (!sessionId) return;

    try {
      await api.post(`/cart/${sessionId}/add`, { product_id: productId, quantity });
      await get().fetchCart();
    } catch (error) {
      console.error('Error adding to cart:', error);
    }
  },

  updateQuantity: async (productId: string, quantity: number) => {
    const { sessionId } = get();
    if (!sessionId) return;

    try {
      if (quantity <= 0) {
        await get().removeFromCart(productId);
      } else {
        await api.put(`/cart/${sessionId}/update`, { product_id: productId, quantity });
        await get().fetchCart();
      }
    } catch (error) {
      console.error('Error updating cart:', error);
    }
  },

  removeFromCart: async (productId: string) => {
    const { sessionId } = get();
    if (!sessionId) return;

    try {
      await api.delete(`/cart/${sessionId}/remove/${productId}`);
      await get().fetchCart();
    } catch (error) {
      console.error('Error removing from cart:', error);
    }
  },

  clearCart: async () => {
    const { sessionId } = get();
    if (!sessionId) return;

    try {
      await api.delete(`/cart/${sessionId}/clear`);
      set({ items: [], products: [] });
    } catch (error) {
      console.error('Error clearing cart:', error);
    }
  },

  getTotalItems: () => {
    const { items } = get();
    return items.reduce((total, item) => total + item.quantity, 0);
  },

  getTotalPrice: () => {
    const { items, products } = get();
    return items.reduce((total, item) => {
      const product = products.find(p => p.id === item.product_id);
      return total + (product ? product.price * item.quantity : 0);
    }, 0);
  },
}));
