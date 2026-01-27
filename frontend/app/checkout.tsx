import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../services/api';
import { useCartStore } from '../store/cartStore';

const timeSlots = [
  '09:00 - 12:00',
  '12:00 - 15:00',
  '15:00 - 18:00',
  '18:00 - 21:00',
];

export default function CheckoutScreen() {
  const router = useRouter();
  const { items, products, getTotalPrice, clearCart } = useCartStore();
  const [isLoading, setIsLoading] = useState(false);

  const [formData, setFormData] = useState({
    fullName: '',
    phone: '',
    address: '',
    city: 'İstanbul',
    district: '',
    notes: '',
  });

  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTimeSlot, setSelectedTimeSlot] = useState('');

  const subtotal = getTotalPrice();
  const deliveryFee = subtotal >= 300 ? 0 : 14.90;
  const total = subtotal + deliveryFee;

  // Generate next 7 days
  const getDeliveryDates = () => {
    const dates = [];
    const today = new Date();
    for (let i = 1; i <= 7; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      dates.push({
        value: date.toISOString().split('T')[0],
        label: date.toLocaleDateString('tr-TR', {
          weekday: 'short',
          day: 'numeric',
          month: 'short',
        }),
      });
    }
    return dates;
  };

  const deliveryDates = getDeliveryDates();

  const handleSubmit = async () => {
    // Validation
    if (!formData.fullName.trim()) {
      Alert.alert('Hata', 'Lütfen adınızı girin');
      return;
    }
    if (!formData.phone.trim()) {
      Alert.alert('Hata', 'Lütfen telefon numaranızı girin');
      return;
    }
    if (!formData.address.trim()) {
      Alert.alert('Hata', 'Lütfen adresinizi girin');
      return;
    }
    if (!formData.district.trim()) {
      Alert.alert('Hata', 'Lütfen ilçe girin');
      return;
    }
    if (!selectedDate) {
      Alert.alert('Hata', 'Lütfen teslimat tarihi seçin');
      return;
    }
    if (!selectedTimeSlot) {
      Alert.alert('Hata', 'Lütfen teslimat saati seçin');
      return;
    }

    setIsLoading(true);

    try {
      const sessionId = await AsyncStorage.getItem('session_id');
      
      const orderData = {
        session_id: sessionId,
        delivery_address: {
          full_name: formData.fullName,
          phone: formData.phone,
          address: formData.address,
          city: formData.city,
          district: formData.district,
          notes: formData.notes,
        },
        delivery_date: selectedDate,
        delivery_time_slot: selectedTimeSlot,
        payment_method: 'cash_on_delivery',
      };

      const response = await api.post('/orders', orderData);
      
      Alert.alert(
        'Sipariş Onaylandı',
        `Sipariş numaranız: #${response.data.id.slice(-6).toUpperCase()}\n\nTeslimat: ${selectedDate} - ${selectedTimeSlot}`,
        [
          {
            text: 'Tamam',
            onPress: () => {
              router.replace('/(tabs)/orders');
            },
          },
        ]
      );
    } catch (error) {
      console.error('Order error:', error);
      Alert.alert('Hata', 'Sipariş oluşturulurken bir hata oluştu');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
            <Ionicons name="close" size={24} color="#333" />
          </TouchableOpacity>
          <Text style={styles.title}>Sipariş Tamamla</Text>
          <View style={styles.placeholder} />
        </View>

        <ScrollView
          style={styles.scrollView}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {/* Delivery Address */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Teslimat Adresi</Text>
            
            <TextInput
              style={styles.input}
              placeholder="Ad Soyad"
              placeholderTextColor="#999"
              value={formData.fullName}
              onChangeText={(text) => setFormData({ ...formData, fullName: text })}
            />
            
            <TextInput
              style={styles.input}
              placeholder="Telefon (05xx xxx xx xx)"
              placeholderTextColor="#999"
              keyboardType="phone-pad"
              value={formData.phone}
              onChangeText={(text) => setFormData({ ...formData, phone: text })}
            />
            
            <TextInput
              style={[styles.input, styles.textArea]}
              placeholder="Adres (Sokak, Bina No, Daire)"
              placeholderTextColor="#999"
              multiline
              numberOfLines={3}
              value={formData.address}
              onChangeText={(text) => setFormData({ ...formData, address: text })}
            />
            
            <View style={styles.row}>
              <TextInput
                style={[styles.input, styles.halfInput]}
                placeholder="İl"
                placeholderTextColor="#999"
                value={formData.city}
                onChangeText={(text) => setFormData({ ...formData, city: text })}
              />
              <TextInput
                style={[styles.input, styles.halfInput]}
                placeholder="İlçe"
                placeholderTextColor="#999"
                value={formData.district}
                onChangeText={(text) => setFormData({ ...formData, district: text })}
              />
            </View>
            
            <TextInput
              style={styles.input}
              placeholder="Sipariş Notu (Opsiyonel)"
              placeholderTextColor="#999"
              value={formData.notes}
              onChangeText={(text) => setFormData({ ...formData, notes: text })}
            />
          </View>

          {/* Delivery Date */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Teslimat Tarihi</Text>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.dateScroll}
            >
              {deliveryDates.map((date) => (
                <TouchableOpacity
                  key={date.value}
                  style={[
                    styles.dateButton,
                    selectedDate === date.value && styles.selectedDateButton,
                  ]}
                  onPress={() => setSelectedDate(date.value)}
                >
                  <Text
                    style={[
                      styles.dateText,
                      selectedDate === date.value && styles.selectedDateText,
                    ]}
                  >
                    {date.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>

          {/* Delivery Time */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Teslimat Saati</Text>
            <View style={styles.timeGrid}>
              {timeSlots.map((slot) => (
                <TouchableOpacity
                  key={slot}
                  style={[
                    styles.timeButton,
                    selectedTimeSlot === slot && styles.selectedTimeButton,
                  ]}
                  onPress={() => setSelectedTimeSlot(slot)}
                >
                  <Ionicons
                    name="time-outline"
                    size={18}
                    color={selectedTimeSlot === slot ? '#fff' : '#666'}
                  />
                  <Text
                    style={[
                      styles.timeText,
                      selectedTimeSlot === slot && styles.selectedTimeText,
                    ]}
                  >
                    {slot}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* Payment Method */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Ödeme Yöntemi</Text>
            <View style={styles.paymentMethod}>
              <Ionicons name="cash-outline" size={24} color="#4CAF50" />
              <View style={styles.paymentInfo}>
                <Text style={styles.paymentTitle}>Kapıda Ödeme</Text>
                <Text style={styles.paymentSubtitle}>Nakit veya kredi kartı ile ödeme</Text>
              </View>
              <Ionicons name="checkmark-circle" size={24} color="#4CAF50" />
            </View>
          </View>

          {/* Order Summary */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Sipariş Özeti</Text>
            <View style={styles.summaryCard}>
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Ürünler ({items.length} adet)</Text>
                <Text style={styles.summaryValue}>{subtotal.toFixed(2)} TL</Text>
              </View>
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Teslimat Ücreti</Text>
                <Text style={[styles.summaryValue, deliveryFee === 0 && styles.freeDelivery]}>
                  {deliveryFee === 0 ? 'Ücretsiz' : `${deliveryFee.toFixed(2)} TL`}
                </Text>
              </View>
              <View style={[styles.summaryRow, styles.totalRow]}>
                <Text style={styles.totalLabel}>Toplam</Text>
                <Text style={styles.totalValue}>{total.toFixed(2)} TL</Text>
              </View>
            </View>
          </View>

          <View style={styles.bottomSpacing} />
        </ScrollView>

        {/* Submit Button */}
        <View style={styles.submitContainer}>
          <TouchableOpacity
            style={styles.submitButton}
            onPress={handleSubmit}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <>
                <Text style={styles.submitButtonText}>Siparişi Onayla</Text>
                <Text style={styles.submitButtonPrice}>{total.toFixed(2)} TL</Text>
              </>
            )}
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
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
  input: {
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 16,
    color: '#333',
    marginBottom: 12,
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  row: {
    flexDirection: 'row',
    gap: 12,
  },
  halfInput: {
    flex: 1,
  },
  dateScroll: {
    gap: 8,
  },
  dateButton: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: '#f5f5f5',
    minWidth: 90,
    alignItems: 'center',
  },
  selectedDateButton: {
    backgroundColor: '#FF6B00',
  },
  dateText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  selectedDateText: {
    color: '#fff',
  },
  timeGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  timeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: '#f5f5f5',
    width: '48%',
  },
  selectedTimeButton: {
    backgroundColor: '#FF6B00',
  },
  timeText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  selectedTimeText: {
    color: '#fff',
  },
  paymentMethod: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    padding: 16,
    borderRadius: 12,
    gap: 12,
  },
  paymentInfo: {
    flex: 1,
  },
  paymentTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  paymentSubtitle: {
    fontSize: 12,
    color: '#888',
    marginTop: 2,
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
  freeDelivery: {
    color: '#4CAF50',
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
    height: 100,
  },
  submitContainer: {
    backgroundColor: '#fff',
    paddingHorizontal: 16,
    paddingVertical: 12,
    paddingBottom: 24,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  submitButton: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#FF6B00',
    paddingHorizontal: 24,
    paddingVertical: 16,
    borderRadius: 12,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  submitButtonPrice: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
