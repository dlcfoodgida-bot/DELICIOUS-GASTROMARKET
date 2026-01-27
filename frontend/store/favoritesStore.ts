import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../services/api';

interface Product {
  id: string;
  name: string;
  name_tr: string;
  price: number;
  original_price?: number;
  image_url: string;
  unit: string;
  is_on_sale?: boolean;
  discount_percent?: number;
}

interface FavoritesState {
  sessionId: string;
  productIds: string[];
  products: Product[];
  isLoading: boolean;
  initSession: () => Promise<void>;
  fetchFavorites: () => Promise<void>;
  toggleFavorite: (productId: string) => Promise<void>;
  isFavorite: (productId: string) => boolean;
}

export const useFavoritesStore = create<FavoritesState>((set, get) => ({
  sessionId: '',
  productIds: [],
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
      await get().fetchFavorites();
    } catch (error) {
      console.error('Error initializing session:', error);
    }
  },

  fetchFavorites: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    
    set({ isLoading: true });
    try {
      const response = await api.get(`/favorites/${sessionId}`);
      set({ 
        productIds: response.data.product_ids || [],
        products: response.data.products || [],
        isLoading: false 
      });
    } catch (error) {
      console.error('Error fetching favorites:', error);
      set({ isLoading: false });
    }
  },

  toggleFavorite: async (productId: string) => {
    const { sessionId, productIds } = get();
    if (!sessionId) return;

    // Optimistic update
    const isFav = productIds.includes(productId);
    set({ 
      productIds: isFav 
        ? productIds.filter(id => id !== productId)
        : [...productIds, productId]
    });

    try {
      await api.post(`/favorites/${sessionId}/toggle/${productId}`);
      await get().fetchFavorites();
    } catch (error) {
      console.error('Error toggling favorite:', error);
      // Revert on error
      set({ productIds });
    }
  },

  isFavorite: (productId: string) => {
    return get().productIds.includes(productId);
  },
}));
