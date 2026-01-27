import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../../services/api';

interface OrderItem {
  product_id: string;
  product_name: string;
  product_name_tr: string;
  price: number;
  quantity: number;
  total: number;
  image_url: string;
}

interface Order {
  id: string;
  items: OrderItem[];
  subtotal: number;
  delivery_fee: number;
  total: number;
  status: string;
  delivery_date: string;
  delivery_time_slot: string;
  delivery_address: {
    full_name: string;
    phone: string;
    address: string;
    city: string;
    district: string;
    notes?: string;
  };
  created_at: string;
}

const statusSteps = [
  { key: 'confirmed', label: 'Onaylandı', icon: 'checkmark-circle' },
  { key: 'preparing', label: 'Hazırlanıyor', icon: 'cube' },
  { key: 'on_the_way', label: 'Yolda', icon: 'bicycle' },
  { key: 'delivered', label: 'Teslim Edildi', icon: 'checkmark-done' },
];

export default function OrderDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [order, setOrder] = useState<Order | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchOrder = async () => {
      try {
        const sessionId = await AsyncStorage.getItem('session_id');
        if (sessionId && id) {
          const response = await api.get(`/orders/${sessionId}/${id}`);
          setOrder(response.data);
        }
      } catch (error) {
        console.error('Error fetching order:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchOrder();
  }, [id]);

  const getStatusIndex = () => {
    if (!order) return 0;
    const index = statusSteps.findIndex((step) => step.key === order.status);
    return index >= 0 ? index : 0;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#FF6B00" />
        </View>
      </SafeAreaView>
    );
  }

  if (!order) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <View style={styles.loadingContainer}>
          <Text>Sipariş bulunamadı</Text>
        </View>
      </SafeAreaView>
    );
  }

  const currentStatusIndex = getStatusIndex();

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.title}>Sipariş Detayı</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Order ID & Date */}
        <View style={styles.section}>
          <View style={styles.orderHeader}>
            <Text style={styles.orderId}>#{order.id.slice(-6).toUpperCase()}</Text>
            <Text style={styles.orderDate}>{formatDate(order.created_at)}</Text>
          </View>
        </View>

        {/* Status Tracker */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Sipariş Durumu</Text>
          <View style={styles.statusTracker}>
            {statusSteps.map((step, index) => (
              <View key={step.key} style={styles.statusStep}>
                <View
                  style={[
                    styles.statusIcon,
                    index <= currentStatusIndex && styles.statusIconActive,
                  ]}
                >
                  <Ionicons
                    name={step.icon as any}
                    size={20}
                    color={index <= currentStatusIndex ? '#fff' : '#ccc'}
                  />
                </View>
                <Text
                  style={[
                    styles.statusLabel,
                    index <= currentStatusIndex && styles.statusLabelActive,
                  ]}
                >
                  {step.label}
                </Text>
                {index < statusSteps.length - 1 && (
                  <View
                    style={[
                      styles.statusLine,
                      index < currentStatusIndex && styles.statusLineActive,
                    ]}
                  />
                )}
              </View>
            ))}
          </View>
        </View>

        {/* Delivery Info */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Teslimat Bilgileri</Text>
          <View style={styles.infoCard}>
            <View style={styles.infoRow}>
              <Ionicons name="calendar-outline" size={20} color="#666" />
              <Text style={styles.infoText}>
                {order.delivery_date} - {order.delivery_time_slot}
              </Text>
            </View>
            <View style={styles.infoRow}>
              <Ionicons name="person-outline" size={20} color="#666" />
              <Text style={styles.infoText}>{order.delivery_address.full_name}</Text>
            </View>
            <View style={styles.infoRow}>
              <Ionicons name="call-outline" size={20} color="#666" />
              <Text style={styles.infoText}>{order.delivery_address.phone}</Text>
            </View>
            <View style={styles.infoRow}>
              <Ionicons name="location-outline" size={20} color="#666" />
              <Text style={styles.infoText}>
                {order.delivery_address.address}, {order.delivery_address.district}/
                {order.delivery_address.city}
              </Text>
            </View>
            {order.delivery_address.notes && (
              <View style={styles.infoRow}>
                <Ionicons name="document-text-outline" size={20} color="#666" />
                <Text style={styles.infoText}>{order.delivery_address.notes}</Text>
              </View>
            )}
          </View>
        </View>

        {/* Order Items */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Ürünler ({order.items.length})</Text>
          {order.items.map((item) => (
            <View key={item.product_id} style={styles.orderItem}>
              <Image source={{ uri: item.image_url }} style={styles.itemImage} />
              <View style={styles.itemInfo}>
                <Text style={styles.itemName} numberOfLines={2}>
                  {item.product_name_tr}
                </Text>
                <Text style={styles.itemQuantity}>
                  {item.quantity} x {item.price.toFixed(2)} TL
                </Text>
              </View>
              <Text style={styles.itemTotal}>{item.total.toFixed(2)} TL</Text>
            </View>
          ))}
        </View>

        {/* Order Summary */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Sipariş Özeti</Text>
          <View style={styles.summaryCard}>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Ara Toplam</Text>
              <Text style={styles.summaryValue}>{order.subtotal.toFixed(2)} TL</Text>
            </View>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Teslimat Ücreti</Text>
              <Text style={styles.summaryValue}>
                {order.delivery_fee === 0 ? 'Ücretsiz' : `${order.delivery_fee.toFixed(2)} TL`}
              </Text>
            </View>
            <View style={[styles.summaryRow, styles.totalRow]}>
              <Text style={styles.totalLabel}>Toplam</Text>
              <Text style={styles.totalValue}>{order.total.toFixed(2)} TL</Text>
            </View>
          </View>
        </View>

        <View style={styles.bottomSpacing} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  backButton: {
    width: 44,
    height: 44,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  placeholder: {
    width: 44,
  },
  scrollView: {
    flex: 1,
  },
  section: {
    backgroundColor: '#fff',
    marginTop: 12,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  orderHeader: {
    alignItems: 'center',
  },
  orderId: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FF6B00',
  },
  orderDate: {
    fontSize: 14,
    color: '#888',
    marginTop: 4,
  },
  statusTracker: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  statusStep: {
    alignItems: 'center',
    flex: 1,
    position: 'relative',
  },
  statusIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#eee',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  statusIconActive: {
    backgroundColor: '#4CAF50',
  },
  statusLabel: {
    fontSize: 11,
    color: '#999',
    textAlign: 'center',
  },
  statusLabelActive: {
    color: '#333',
    fontWeight: '500',
  },
  statusLine: {
    position: 'absolute',
    top: 20,
    left: '60%',
    right: '-40%',
    height: 2,
    backgroundColor: '#eee',
    zIndex: -1,
  },
  statusLineActive: {
    backgroundColor: '#4CAF50',
  },
  infoCard: {
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
    padding: 16,
    gap: 12,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
  },
  orderItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  itemImage: {
    width: 60,
    height: 60,
    borderRadius: 8,
    backgroundColor: '#f5f5f5',
  },
  itemInfo: {
    flex: 1,
    marginLeft: 12,
  },
  itemName: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  itemQuantity: {
    fontSize: 12,
    color: '#888',
    marginTop: 4,
  },
  itemTotal: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#FF6B00',
  },
  summaryCard: {
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
    padding: 16,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  summaryLabel: {
    fontSize: 14,
    color: '#666',
  },
  summaryValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  totalRow: {
    borderTopWidth: 1,
    borderTopColor: '#ddd',
    paddingTop: 12,
    marginBottom: 0,
  },
  totalLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  totalValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FF6B00',
  },
  bottomSpacing: {
    height: 24,
  },
});
