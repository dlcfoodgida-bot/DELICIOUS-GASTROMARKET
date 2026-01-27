import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useQuery } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { api } from '../../services/api';
import { useCartStore } from '../../store/cartStore';
import { useFavoritesStore } from '../../store/favoritesStore';
import ProductCard from '../../components/ProductCard';
import CategoryCard from '../../components/CategoryCard';
import BannerCarousel from '../../components/BannerCarousel';

export default function HomeScreen() {
  const router = useRouter();
  const initCartSession = useCartStore((state) => state.initSession);
  const initFavoritesSession = useFavoritesStore((state) => state.initSession);

  useEffect(() => {
    initCartSession();
    initFavoritesSession();
  }, []);

  const { data: banners, isLoading: bannersLoading } = useQuery({
    queryKey: ['banners'],
    queryFn: async () => {
      const response = await api.get('/banners');
      return response.data;
    },
  });

  const { data: categories, isLoading: categoriesLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await api.get('/categories');
      return response.data;
    },
  });

  const { data: featuredProducts, isLoading: featuredLoading, refetch: refetchFeatured } = useQuery({
    queryKey: ['products', 'featured'],
    queryFn: async () => {
      const response = await api.get('/products?featured=true');
      return response.data;
    },
  });

  const { data: saleProducts, isLoading: saleLoading, refetch: refetchSale } = useQuery({
    queryKey: ['products', 'on_sale'],
    queryFn: async () => {
      const response = await api.get('/products?on_sale=true');
      return response.data;
    },
  });

  const [refreshing, setRefreshing] = React.useState(false);

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([refetchFeatured(), refetchSale()]);
    setRefreshing(false);
  };

  const isLoading = bannersLoading || categoriesLoading || featuredLoading || saleLoading;

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Merhaba!</Text>
          <Text style={styles.title}>Migros Sanal Market</Text>
        </View>
        <TouchableOpacity style={styles.notificationButton}>
          <Ionicons name="notifications-outline" size={24} color="#333" />
        </TouchableOpacity>
      </View>

      {/* Search Bar */}
      <TouchableOpacity
        style={styles.searchContainer}
        onPress={() => router.push('/search')}
        activeOpacity={0.8}
      >
        <Ionicons name="search" size={20} color="#888" />
        <Text style={styles.searchPlaceholder}>Ürün, kategori ara...</Text>
      </TouchableOpacity>

      {isLoading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#FF6B00" />
        </View>
      ) : (
        <ScrollView
          style={styles.scrollView}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              colors={['#FF6B00']}
            />
          }
        >
          {/* Banners */}
          {banners && banners.length > 0 && (
            <BannerCarousel banners={banners} />
          )}

          {/* Categories */}
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>Kategoriler</Text>
              <TouchableOpacity onPress={() => router.push('/(tabs)/categories')}>
                <Text style={styles.seeAll}>Tümünü Gör</Text>
              </TouchableOpacity>
            </View>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.categoryScroll}
            >
              {categories?.slice(0, 8).map((category: any) => (
                <CategoryCard key={category.id} category={category} compact />
              ))}
            </ScrollView>
          </View>

          {/* Featured Products */}
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>Öne Çıkan Ürünler</Text>
              <TouchableOpacity>
                <Text style={styles.seeAll}>Tümünü Gör</Text>
              </TouchableOpacity>
            </View>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.productScroll}
            >
              {featuredProducts?.map((product: any) => (
                <ProductCard key={product.id} product={product} compact />
              ))}
            </ScrollView>
          </View>

          {/* Sale Products */}
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <View style={styles.saleTitleContainer}>
                <Ionicons name="pricetag" size={20} color="#FF4444" />
                <Text style={[styles.sectionTitle, styles.saleTitle]}>Fırsatlar</Text>
              </View>
              <TouchableOpacity>
                <Text style={styles.seeAll}>Tümünü Gör</Text>
              </TouchableOpacity>
            </View>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.productScroll}
            >
              {saleProducts?.map((product: any) => (
                <ProductCard key={product.id} product={product} compact />
              ))}
            </ScrollView>
          </View>

          <View style={styles.bottomSpacing} />
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  greeting: {
    fontSize: 14,
    color: '#666',
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#FF6B00',
  },
  notificationButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginBottom: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 2,
  },
  searchPlaceholder: {
    marginLeft: 12,
    fontSize: 15,
    color: '#888',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollView: {
    flex: 1,
  },
  section: {
    marginTop: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  saleTitleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  saleTitle: {
    color: '#FF4444',
  },
  seeAll: {
    fontSize: 14,
    color: '#FF6B00',
    fontWeight: '600',
  },
  categoryScroll: {
    paddingHorizontal: 16,
  },
  productScroll: {
    paddingHorizontal: 16,
  },
  bottomSpacing: {
    height: 24,
  },
});
