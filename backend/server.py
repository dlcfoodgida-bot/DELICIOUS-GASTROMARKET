from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from bson import ObjectId

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Helper function for ObjectId serialization
def serialize_doc(doc):
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return doc

# ==================== MODELS ====================

class Category(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    name_tr: str  # Turkish name
    icon: str  # Expo vector icon name
    image_url: str
    color: str
    product_count: int = 0

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    name_tr: str
    description: str
    description_tr: str
    price: float
    original_price: Optional[float] = None  # For discounted items
    category_id: str
    image_url: str
    unit: str  # kg, adet, litre, etc.
    stock: int = 100
    is_featured: bool = False
    is_on_sale: bool = False
    discount_percent: Optional[int] = None
    rating: float = 4.5
    review_count: int = 0

class CartItem(BaseModel):
    product_id: str
    quantity: int

class Cart(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    items: List[CartItem] = []
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CartItemAdd(BaseModel):
    product_id: str
    quantity: int = 1

class CartItemUpdate(BaseModel):
    product_id: str
    quantity: int

class DeliveryAddress(BaseModel):
    full_name: str
    phone: str
    address: str
    city: str
    district: str
    notes: Optional[str] = None

class OrderCreate(BaseModel):
    session_id: str
    delivery_address: DeliveryAddress
    delivery_date: str
    delivery_time_slot: str
    payment_method: str = "cash_on_delivery"

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    items: List[dict]
    subtotal: float
    delivery_fee: float = 14.90
    total: float
    delivery_address: DeliveryAddress
    delivery_date: str
    delivery_time_slot: str
    payment_method: str
    status: str = "pending"  # pending, confirmed, preparing, on_the_way, delivered
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Banner(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    subtitle: str
    image_url: str
    background_color: str
    link_type: str  # category, product, promo
    link_id: Optional[str] = None

class Favorite(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    product_ids: List[str] = []

# ==================== SEED DATA ====================

async def seed_database():
    """Seed the database with initial categories, products, and banners"""
    
    # Check if already seeded
    existing_categories = await db.categories.count_documents({})
    if existing_categories > 0:
        logger.info("Database already seeded")
        return
    
    logger.info("Seeding database...")
    
    # Categories
    categories = [
        {
            "id": "cat_fruits_vegetables",
            "name": "Fruits & Vegetables",
            "name_tr": "Meyve & Sebze",
            "icon": "leaf",
            "image_url": "https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=400",
            "color": "#4CAF50",
            "product_count": 12
        },
        {
            "id": "cat_dairy",
            "name": "Dairy & Eggs",
            "name_tr": "Süt & Kahvaltılık",
            "icon": "water",
            "image_url": "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=400",
            "color": "#2196F3",
            "product_count": 10
        },
        {
            "id": "cat_meat",
            "name": "Meat & Seafood",
            "name_tr": "Et & Deniz Ürünleri",
            "icon": "restaurant",
            "image_url": "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=400",
            "color": "#F44336",
            "product_count": 8
        },
        {
            "id": "cat_bakery",
            "name": "Bakery",
            "name_tr": "Ekmek & Pasta",
            "icon": "cafe",
            "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400",
            "color": "#FF9800",
            "product_count": 8
        },
        {
            "id": "cat_beverages",
            "name": "Beverages",
            "name_tr": "İçecekler",
            "icon": "beer",
            "image_url": "https://images.unsplash.com/photo-1534353473418-4cfa6c56fd38?w=400",
            "color": "#9C27B0",
            "product_count": 10
        },
        {
            "id": "cat_snacks",
            "name": "Snacks & Sweets",
            "name_tr": "Atıştırmalık",
            "icon": "pizza",
            "image_url": "https://images.unsplash.com/photo-1621939514649-280e2ee25f60?w=400",
            "color": "#E91E63",
            "product_count": 8
        },
        {
            "id": "cat_frozen",
            "name": "Frozen Foods",
            "name_tr": "Dondurulmuş",
            "icon": "snow",
            "image_url": "https://images.unsplash.com/photo-1579954115545-a95591f28bfc?w=400",
            "color": "#00BCD4",
            "product_count": 6
        },
        {
            "id": "cat_household",
            "name": "Household",
            "name_tr": "Ev & Temizlik",
            "icon": "home",
            "image_url": "https://images.unsplash.com/photo-1585421514738-01798e348b17?w=400",
            "color": "#607D8B",
            "product_count": 8
        }
    ]
    
    await db.categories.insert_many(categories)
    
    # Products
    products = [
        # Fruits & Vegetables
        {"id": "prod_1", "name": "Fresh Tomatoes", "name_tr": "Taze Domates", "description": "Fresh organic tomatoes", "description_tr": "Taze organik domates", "price": 24.90, "original_price": 29.90, "category_id": "cat_fruits_vegetables", "image_url": "https://images.unsplash.com/photo-1546470427-227c7e36e58f?w=400", "unit": "kg", "stock": 100, "is_featured": True, "is_on_sale": True, "discount_percent": 17, "rating": 4.7, "review_count": 128},
        {"id": "prod_2", "name": "Bananas", "name_tr": "Muz", "description": "Sweet yellow bananas", "description_tr": "Tatlı sarı muz", "price": 44.90, "category_id": "cat_fruits_vegetables", "image_url": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=400", "unit": "kg", "stock": 100, "is_featured": True, "rating": 4.8, "review_count": 256},
        {"id": "prod_3", "name": "Fresh Cucumbers", "name_tr": "Taze Salatalık", "description": "Crispy fresh cucumbers", "description_tr": "Çıtır taze salatalık", "price": 19.90, "category_id": "cat_fruits_vegetables", "image_url": "https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=400", "unit": "kg", "stock": 100, "rating": 4.5, "review_count": 89},
        {"id": "prod_4", "name": "Red Apples", "name_tr": "Kırmızı Elma", "description": "Sweet red apples", "description_tr": "Tatlı kırmızı elma", "price": 34.90, "category_id": "cat_fruits_vegetables", "image_url": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400", "unit": "kg", "stock": 100, "is_featured": True, "rating": 4.6, "review_count": 167},
        {"id": "prod_5", "name": "Fresh Broccoli", "name_tr": "Taze Brokoli", "description": "Healthy green broccoli", "description_tr": "Sağlıklı yeşil brokoli", "price": 29.90, "original_price": 39.90, "category_id": "cat_fruits_vegetables", "image_url": "https://images.unsplash.com/photo-1583663848850-46af132dc08e?w=400", "unit": "kg", "stock": 100, "is_on_sale": True, "discount_percent": 25, "rating": 4.4, "review_count": 72},
        {"id": "prod_6", "name": "Fresh Oranges", "name_tr": "Taze Portakal", "description": "Juicy oranges", "description_tr": "Sulu portakal", "price": 29.90, "category_id": "cat_fruits_vegetables", "image_url": "https://images.unsplash.com/photo-1547514701-42782101795e?w=400", "unit": "kg", "stock": 100, "rating": 4.7, "review_count": 145},
        
        # Dairy & Eggs
        {"id": "prod_7", "name": "Fresh Milk", "name_tr": "Taze Süt", "description": "Fresh whole milk 1L", "description_tr": "Taze tam yağlı süt 1L", "price": 32.90, "category_id": "cat_dairy", "image_url": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400", "unit": "adet", "stock": 100, "is_featured": True, "rating": 4.8, "review_count": 312},
        {"id": "prod_8", "name": "Free Range Eggs", "name_tr": "Serbest Gezen Yumurta", "description": "Pack of 15 eggs", "description_tr": "15'li yumurta", "price": 89.90, "original_price": 99.90, "category_id": "cat_dairy", "image_url": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=400", "unit": "adet", "stock": 100, "is_on_sale": True, "discount_percent": 10, "rating": 4.9, "review_count": 428},
        {"id": "prod_9", "name": "Turkish White Cheese", "name_tr": "Beyaz Peynir", "description": "Traditional white cheese", "description_tr": "Geleneksel beyaz peynir", "price": 149.90, "category_id": "cat_dairy", "image_url": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=400", "unit": "kg", "stock": 100, "is_featured": True, "rating": 4.7, "review_count": 234},
        {"id": "prod_10", "name": "Natural Yogurt", "name_tr": "Doğal Yoğurt", "description": "Creamy natural yogurt 1kg", "description_tr": "Kremsi doğal yoğurt 1kg", "price": 54.90, "category_id": "cat_dairy", "image_url": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400", "unit": "adet", "stock": 100, "rating": 4.6, "review_count": 189},
        {"id": "prod_11", "name": "Butter", "name_tr": "Tereyağı", "description": "Pure butter 250g", "description_tr": "Saf tereyağı 250g", "price": 79.90, "category_id": "cat_dairy", "image_url": "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=400", "unit": "adet", "stock": 100, "rating": 4.8, "review_count": 156},
        
        # Meat & Seafood
        {"id": "prod_12", "name": "Chicken Breast", "name_tr": "Tavuk Göğsü", "description": "Fresh chicken breast", "description_tr": "Taze tavuk göğsü", "price": 129.90, "category_id": "cat_meat", "image_url": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=400", "unit": "kg", "stock": 100, "is_featured": True, "rating": 4.6, "review_count": 198},
        {"id": "prod_13", "name": "Ground Beef", "name_tr": "Dana Kıyma", "description": "Fresh ground beef", "description_tr": "Taze dana kıyma", "price": 249.90, "original_price": 279.90, "category_id": "cat_meat", "image_url": "https://images.unsplash.com/photo-1602470520998-f4a52199a3d6?w=400", "unit": "kg", "stock": 100, "is_on_sale": True, "discount_percent": 11, "rating": 4.7, "review_count": 267},
        {"id": "prod_14", "name": "Fresh Salmon", "name_tr": "Taze Somon", "description": "Atlantic salmon fillet", "description_tr": "Atlantik somon fileto", "price": 349.90, "category_id": "cat_meat", "image_url": "https://images.unsplash.com/photo-1574781330855-d0db8cc6a79c?w=400", "unit": "kg", "stock": 100, "is_featured": True, "rating": 4.8, "review_count": 145},
        {"id": "prod_15", "name": "Lamb Chops", "name_tr": "Kuzu Pirzola", "description": "Premium lamb chops", "description_tr": "Premium kuzu pirzola", "price": 399.90, "category_id": "cat_meat", "image_url": "https://images.unsplash.com/photo-1603048297172-c92544798d5a?w=400", "unit": "kg", "stock": 100, "rating": 4.9, "review_count": 89},
        
        # Bakery
        {"id": "prod_16", "name": "Fresh Bread", "name_tr": "Taze Ekmek", "description": "Daily fresh bread", "description_tr": "Günlük taze ekmek", "price": 12.90, "category_id": "cat_bakery", "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400", "unit": "adet", "stock": 100, "is_featured": True, "rating": 4.7, "review_count": 534},
        {"id": "prod_17", "name": "Croissant", "name_tr": "Kruvasan", "description": "Buttery croissant", "description_tr": "Tereyağlı kruvasan", "price": 24.90, "category_id": "cat_bakery", "image_url": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=400", "unit": "adet", "stock": 100, "rating": 4.8, "review_count": 287},
        {"id": "prod_18", "name": "Turkish Simit", "name_tr": "Simit", "description": "Traditional Turkish simit", "description_tr": "Geleneksel Türk simidi", "price": 9.90, "original_price": 12.90, "category_id": "cat_bakery", "image_url": "https://images.unsplash.com/photo-1600147131759-880e94a6185f?w=400", "unit": "adet", "stock": 100, "is_on_sale": True, "discount_percent": 23, "rating": 4.9, "review_count": 412},
        {"id": "prod_19", "name": "Chocolate Cake", "name_tr": "Çikolatalı Pasta", "description": "Rich chocolate cake", "description_tr": "Bol çikolatalı pasta", "price": 189.90, "category_id": "cat_bakery", "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400", "unit": "adet", "stock": 100, "rating": 4.8, "review_count": 167},
        
        # Beverages
        {"id": "prod_20", "name": "Orange Juice", "name_tr": "Portakal Suyu", "description": "Fresh orange juice 1L", "description_tr": "Taze portakal suyu 1L", "price": 34.90, "category_id": "cat_beverages", "image_url": "https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=400", "unit": "adet", "stock": 100, "is_featured": True, "rating": 4.6, "review_count": 198},
        {"id": "prod_21", "name": "Turkish Tea", "name_tr": "Türk Çayı", "description": "Premium black tea 500g", "description_tr": "Premium siyah çay 500g", "price": 89.90, "original_price": 109.90, "category_id": "cat_beverages", "image_url": "https://images.unsplash.com/photo-1571934811356-5cc061b6821f?w=400", "unit": "adet", "stock": 100, "is_on_sale": True, "discount_percent": 18, "rating": 4.9, "review_count": 567},
        {"id": "prod_22", "name": "Mineral Water", "name_tr": "Maden Suyu", "description": "Natural mineral water 6x1.5L", "description_tr": "Doğal maden suyu 6x1.5L", "price": 49.90, "category_id": "cat_beverages", "image_url": "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=400", "unit": "adet", "stock": 100, "rating": 4.5, "review_count": 234},
        {"id": "prod_23", "name": "Turkish Coffee", "name_tr": "Türk Kahvesi", "description": "Traditional Turkish coffee 250g", "description_tr": "Geleneksel Türk kahvesi 250g", "price": 79.90, "category_id": "cat_beverages", "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=400", "unit": "adet", "stock": 100, "is_featured": True, "rating": 4.9, "review_count": 423},
        
        # Snacks
        {"id": "prod_24", "name": "Mixed Nuts", "name_tr": "Karışık Kuruyemiş", "description": "Premium mixed nuts 500g", "description_tr": "Premium karışık kuruyemiş 500g", "price": 149.90, "category_id": "cat_snacks", "image_url": "https://images.unsplash.com/photo-1536591102973-08f21af396f8?w=400", "unit": "adet", "stock": 100, "is_featured": True, "rating": 4.7, "review_count": 289},
        {"id": "prod_25", "name": "Chocolate Bar", "name_tr": "Çikolata", "description": "Premium milk chocolate", "description_tr": "Premium sütlü çikolata", "price": 29.90, "original_price": 34.90, "category_id": "cat_snacks", "image_url": "https://images.unsplash.com/photo-1606312619070-d48b4c652a52?w=400", "unit": "adet", "stock": 100, "is_on_sale": True, "discount_percent": 14, "rating": 4.8, "review_count": 356},
        {"id": "prod_26", "name": "Turkish Delight", "name_tr": "Lokum", "description": "Traditional Turkish delight", "description_tr": "Geleneksel Türk lokumu", "price": 69.90, "category_id": "cat_snacks", "image_url": "https://images.unsplash.com/photo-1576097449798-7c7f90e1248a?w=400", "unit": "adet", "stock": 100, "rating": 4.9, "review_count": 234},
        
        # Frozen Foods
        {"id": "prod_27", "name": "Frozen Pizza", "name_tr": "Dondurulmuş Pizza", "description": "Margherita pizza", "description_tr": "Margherita pizza", "price": 54.90, "category_id": "cat_frozen", "image_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400", "unit": "adet", "stock": 100, "is_featured": True, "rating": 4.5, "review_count": 178},
        {"id": "prod_28", "name": "Ice Cream", "name_tr": "Dondurma", "description": "Vanilla ice cream 1L", "description_tr": "Vanilyalı dondurma 1L", "price": 89.90, "original_price": 99.90, "category_id": "cat_frozen", "image_url": "https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=400", "unit": "adet", "stock": 100, "is_on_sale": True, "discount_percent": 10, "rating": 4.8, "review_count": 267},
        {"id": "prod_29", "name": "Frozen Vegetables", "name_tr": "Dondurulmuş Sebze", "description": "Mixed frozen vegetables 1kg", "description_tr": "Karışık dondurulmuş sebze 1kg", "price": 44.90, "category_id": "cat_frozen", "image_url": "https://images.unsplash.com/photo-1597362925123-77861d3fbac7?w=400", "unit": "adet", "stock": 100, "rating": 4.4, "review_count": 123},
        
        # Household
        {"id": "prod_30", "name": "Dish Soap", "name_tr": "Bulaşık Deterjanı", "description": "Liquid dish soap 1L", "description_tr": "Sıvı bulaşık deterjanı 1L", "price": 39.90, "category_id": "cat_household", "image_url": "https://images.unsplash.com/photo-1585421514738-01798e348b17?w=400", "unit": "adet", "stock": 100, "rating": 4.5, "review_count": 156},
        {"id": "prod_31", "name": "Laundry Detergent", "name_tr": "Çamaşır Deterjanı", "description": "Washing powder 4kg", "description_tr": "Toz deterjan 4kg", "price": 149.90, "original_price": 179.90, "category_id": "cat_household", "image_url": "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?w=400", "unit": "adet", "stock": 100, "is_on_sale": True, "discount_percent": 17, "rating": 4.6, "review_count": 234},
        {"id": "prod_32", "name": "Paper Towels", "name_tr": "Kağıt Havlu", "description": "Pack of 8 rolls", "description_tr": "8'li paket", "price": 79.90, "category_id": "cat_household", "image_url": "https://images.unsplash.com/photo-1584556812952-905ffd0c611a?w=400", "unit": "adet", "stock": 100, "rating": 4.4, "review_count": 189},
    ]
    
    await db.products.insert_many(products)
    
    # Banners
    banners = [
        {
            "id": "banner_1",
            "title": "Fresh Vegetables",
            "subtitle": "Up to 25% off on fresh produce",
            "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=800",
            "background_color": "#4CAF50",
            "link_type": "category",
            "link_id": "cat_fruits_vegetables"
        },
        {
            "id": "banner_2",
            "title": "Dairy Week",
            "subtitle": "Special offers on milk & cheese",
            "image_url": "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=800",
            "background_color": "#2196F3",
            "link_type": "category",
            "link_id": "cat_dairy"
        },
        {
            "id": "banner_3",
            "title": "Free Delivery",
            "subtitle": "On orders over 300 TL",
            "image_url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=800",
            "background_color": "#FF5722",
            "link_type": "promo",
            "link_id": None
        }
    ]
    
    await db.banners.insert_many(banners)
    
    logger.info("Database seeded successfully!")

# ==================== ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "Migros Market API", "status": "running"}

# Categories
@api_router.get("/categories")
async def get_categories():
    categories = await db.categories.find().to_list(100)
    return [serialize_doc(cat) for cat in categories]

@api_router.get("/categories/{category_id}")
async def get_category(category_id: str):
    category = await db.categories.find_one({"id": category_id})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return serialize_doc(category)

# Products
@api_router.get("/products")
async def get_products(
    category_id: Optional[str] = None,
    search: Optional[str] = None,
    featured: Optional[bool] = None,
    on_sale: Optional[bool] = None,
    limit: int = Query(default=50, le=100),
    skip: int = 0
):
    query = {}
    
    if category_id:
        query["category_id"] = category_id
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"name_tr": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"description_tr": {"$regex": search, "$options": "i"}}
        ]
    
    if featured:
        query["is_featured"] = True
    
    if on_sale:
        query["is_on_sale"] = True
    
    products = await db.products.find(query).skip(skip).limit(limit).to_list(limit)
    return [serialize_doc(prod) for prod in products]

@api_router.get("/products/{product_id}")
async def get_product(product_id: str):
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return serialize_doc(product)

# Banners
@api_router.get("/banners")
async def get_banners():
    banners = await db.banners.find().to_list(20)
    return [serialize_doc(banner) for banner in banners]

# Cart
@api_router.get("/cart/{session_id}")
async def get_cart(session_id: str):
    cart = await db.carts.find_one({"session_id": session_id})
    if not cart:
        return {"session_id": session_id, "items": [], "products": []}
    
    # Get product details for cart items
    product_ids = [item["product_id"] for item in cart.get("items", [])]
    products = await db.products.find({"id": {"$in": product_ids}}).to_list(100)
    products_map = {p["id"]: serialize_doc(p) for p in products}
    
    cart_with_products = {
        "session_id": session_id,
        "items": cart.get("items", []),
        "products": [products_map.get(item["product_id"]) for item in cart.get("items", []) if products_map.get(item["product_id"])]
    }
    
    return cart_with_products

@api_router.post("/cart/{session_id}/add")
async def add_to_cart(session_id: str, item: CartItemAdd):
    cart = await db.carts.find_one({"session_id": session_id})
    
    if not cart:
        cart = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "items": [],
            "updated_at": datetime.utcnow()
        }
    
    # Check if product exists
    product = await db.products.find_one({"id": item.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update or add item
    items = cart.get("items", [])
    existing_item = next((i for i in items if i["product_id"] == item.product_id), None)
    
    if existing_item:
        existing_item["quantity"] += item.quantity
    else:
        items.append({"product_id": item.product_id, "quantity": item.quantity})
    
    cart["items"] = items
    cart["updated_at"] = datetime.utcnow()
    
    await db.carts.update_one(
        {"session_id": session_id},
        {"$set": cart},
        upsert=True
    )
    
    return {"message": "Item added to cart", "cart": cart}

@api_router.put("/cart/{session_id}/update")
async def update_cart_item(session_id: str, item: CartItemUpdate):
    cart = await db.carts.find_one({"session_id": session_id})
    
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    items = cart.get("items", [])
    
    if item.quantity <= 0:
        # Remove item
        items = [i for i in items if i["product_id"] != item.product_id]
    else:
        # Update quantity
        existing_item = next((i for i in items if i["product_id"] == item.product_id), None)
        if existing_item:
            existing_item["quantity"] = item.quantity
        else:
            raise HTTPException(status_code=404, detail="Item not in cart")
    
    cart["items"] = items
    cart["updated_at"] = datetime.utcnow()
    
    await db.carts.update_one(
        {"session_id": session_id},
        {"$set": cart}
    )
    
    return {"message": "Cart updated", "cart": cart}

@api_router.delete("/cart/{session_id}/remove/{product_id}")
async def remove_from_cart(session_id: str, product_id: str):
    cart = await db.carts.find_one({"session_id": session_id})
    
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    items = [i for i in cart.get("items", []) if i["product_id"] != product_id]
    cart["items"] = items
    cart["updated_at"] = datetime.utcnow()
    
    await db.carts.update_one(
        {"session_id": session_id},
        {"$set": cart}
    )
    
    return {"message": "Item removed from cart"}

@api_router.delete("/cart/{session_id}/clear")
async def clear_cart(session_id: str):
    await db.carts.update_one(
        {"session_id": session_id},
        {"$set": {"items": [], "updated_at": datetime.utcnow()}}
    )
    return {"message": "Cart cleared"}

# Favorites
@api_router.get("/favorites/{session_id}")
async def get_favorites(session_id: str):
    favorite = await db.favorites.find_one({"session_id": session_id})
    
    if not favorite:
        return {"session_id": session_id, "product_ids": [], "products": []}
    
    # Get product details
    products = await db.products.find({"id": {"$in": favorite.get("product_ids", [])}}).to_list(100)
    
    return {
        "session_id": session_id,
        "product_ids": favorite.get("product_ids", []),
        "products": [serialize_doc(p) for p in products]
    }

@api_router.post("/favorites/{session_id}/toggle/{product_id}")
async def toggle_favorite(session_id: str, product_id: str):
    # Check if product exists
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    favorite = await db.favorites.find_one({"session_id": session_id})
    
    if not favorite:
        favorite = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "product_ids": []
        }
    
    product_ids = favorite.get("product_ids", [])
    
    if product_id in product_ids:
        product_ids.remove(product_id)
        is_favorite = False
    else:
        product_ids.append(product_id)
        is_favorite = True
    
    favorite["product_ids"] = product_ids
    
    await db.favorites.update_one(
        {"session_id": session_id},
        {"$set": favorite},
        upsert=True
    )
    
    return {"message": "Favorite toggled", "is_favorite": is_favorite}

# Orders
@api_router.post("/orders")
async def create_order(order_data: OrderCreate):
    # Get cart
    cart = await db.carts.find_one({"session_id": order_data.session_id})
    
    if not cart or not cart.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Get products and calculate totals
    product_ids = [item["product_id"] for item in cart["items"]]
    products = await db.products.find({"id": {"$in": product_ids}}).to_list(100)
    products_map = {p["id"]: p for p in products}
    
    order_items = []
    subtotal = 0
    
    for item in cart["items"]:
        product = products_map.get(item["product_id"])
        if product:
            item_total = product["price"] * item["quantity"]
            subtotal += item_total
            order_items.append({
                "product_id": item["product_id"],
                "product_name": product["name"],
                "product_name_tr": product["name_tr"],
                "price": product["price"],
                "quantity": item["quantity"],
                "total": item_total,
                "image_url": product["image_url"]
            })
    
    delivery_fee = 14.90 if subtotal < 300 else 0
    total = subtotal + delivery_fee
    
    order = {
        "id": str(uuid.uuid4()),
        "session_id": order_data.session_id,
        "items": order_items,
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "total": total,
        "delivery_address": order_data.delivery_address.dict(),
        "delivery_date": order_data.delivery_date,
        "delivery_time_slot": order_data.delivery_time_slot,
        "payment_method": order_data.payment_method,
        "status": "confirmed",
        "created_at": datetime.utcnow()
    }
    
    await db.orders.insert_one(order)
    
    # Clear cart after order
    await db.carts.update_one(
        {"session_id": order_data.session_id},
        {"$set": {"items": [], "updated_at": datetime.utcnow()}}
    )
    
    return serialize_doc(order)

@api_router.get("/orders/{session_id}")
async def get_orders(session_id: str):
    orders = await db.orders.find({"session_id": session_id}).sort("created_at", -1).to_list(100)
    return [serialize_doc(order) for order in orders]

@api_router.get("/orders/{session_id}/{order_id}")
async def get_order(session_id: str, order_id: str):
    order = await db.orders.find_one({"id": order_id, "session_id": session_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return serialize_doc(order)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await seed_database()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
