import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

const { width } = Dimensions.get('window');
const cardWidth = (width - 48) / 2;

interface Category {
  id: string;
  name: string;
  name_tr: string;
  icon: string;
  image_url: string;
  color: string;
  product_count: number;
}

interface CategoryCardProps {
  category: Category;
  compact?: boolean;
}

export default function CategoryCard({ category, compact = false }: CategoryCardProps) {
  const router = useRouter();

  const handlePress = () => {
    router.push(`/category/${category.id}`);
  };

  if (compact) {
    return (
      <TouchableOpacity
        style={styles.compactContainer}
        onPress={handlePress}
        activeOpacity={0.8}
      >
        <View style={[styles.compactIcon, { backgroundColor: category.color + '20' }]}>
          <Ionicons name={category.icon as any} size={24} color={category.color} />
        </View>
        <Text style={styles.compactName} numberOfLines={2}>
          {category.name_tr}
        </Text>
      </TouchableOpacity>
    );
  }

  return (
    <TouchableOpacity
      style={styles.container}
      onPress={handlePress}
      activeOpacity={0.9}
    >
      <Image
        source={{ uri: category.image_url }}
        style={styles.image}
        resizeMode="cover"
      />
      <View style={[styles.overlay, { backgroundColor: category.color + 'CC' }]}>
        <Ionicons name={category.icon as any} size={32} color="#fff" />
        <Text style={styles.name}>{category.name_tr}</Text>
        <Text style={styles.count}>{category.product_count} ürün</Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    width: cardWidth,
    height: 140,
    borderRadius: 12,
    overflow: 'hidden',
    marginBottom: 16,
  },
  image: {
    width: '100%',
    height: '100%',
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  name: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 8,
    textAlign: 'center',
  },
  count: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.9)',
    marginTop: 4,
  },
  compactContainer: {
    alignItems: 'center',
    width: 80,
    marginRight: 12,
  },
  compactIcon: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  compactName: {
    fontSize: 12,
    color: '#333',
    textAlign: 'center',
    fontWeight: '500',
  },
});
