#!/usr/bin/env python3
"""
Backend API Testing for Migros Sanal Market
Tests all backend endpoints with comprehensive scenarios
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Backend URL from environment
BACKEND_URL = "https://online-grocery.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_session_id = "test_session_123"
        self.test_session_id_2 = "test_session_456"
        self.results = []
        
    def log_result(self, test_name, success, message, response_data=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_data": response_data
        })
        
    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Migros" in data["message"]:
                    self.log_result("API Root", True, f"API is running: {data['message']}")
                    return True
                else:
                    self.log_result("API Root", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_result("API Root", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("API Root", False, f"Connection error: {str(e)}")
            return False
    
    def test_categories_api(self):
        """Test Categories API endpoints"""
        print("\n=== Testing Categories API ===")
        
        # Test GET /api/categories
        try:
            response = self.session.get(f"{BACKEND_URL}/categories")
            if response.status_code == 200:
                categories = response.json()
                if isinstance(categories, list) and len(categories) == 8:
                    self.log_result("GET /categories", True, f"Retrieved {len(categories)} categories")
                    
                    # Test specific category
                    cat_found = False
                    for cat in categories:
                        if cat.get("id") == "cat_fruits_vegetables":
                            cat_found = True
                            break
                    
                    if cat_found:
                        self.log_result("Categories Content", True, "Found cat_fruits_vegetables category")
                    else:
                        self.log_result("Categories Content", False, "cat_fruits_vegetables not found")
                        
                else:
                    self.log_result("GET /categories", False, f"Expected 8 categories, got {len(categories) if isinstance(categories, list) else 'non-list'}")
            else:
                self.log_result("GET /categories", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("GET /categories", False, f"Error: {str(e)}")
        
        # Test GET /api/categories/{category_id}
        try:
            response = self.session.get(f"{BACKEND_URL}/categories/cat_fruits_vegetables")
            if response.status_code == 200:
                category = response.json()
                if category.get("id") == "cat_fruits_vegetables" and category.get("name_tr"):
                    self.log_result("GET /categories/{id}", True, f"Retrieved category: {category['name_tr']}")
                else:
                    self.log_result("GET /categories/{id}", False, f"Invalid category data: {category}")
            else:
                self.log_result("GET /categories/{id}", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("GET /categories/{id}", False, f"Error: {str(e)}")
    
    def test_products_api(self):
        """Test Products API endpoints"""
        print("\n=== Testing Products API ===")
        
        # Test GET /api/products (all products)
        try:
            response = self.session.get(f"{BACKEND_URL}/products")
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list) and len(products) > 0:
                    self.log_result("GET /products", True, f"Retrieved {len(products)} products")
                else:
                    self.log_result("GET /products", False, f"No products returned or invalid format")
            else:
                self.log_result("GET /products", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("GET /products", False, f"Error: {str(e)}")
        
        # Test GET /api/products?featured=true
        try:
            response = self.session.get(f"{BACKEND_URL}/products?featured=true")
            if response.status_code == 200:
                featured_products = response.json()
                if isinstance(featured_products, list):
                    featured_count = len([p for p in featured_products if p.get("is_featured")])
                    if featured_count == len(featured_products):
                        self.log_result("GET /products?featured=true", True, f"Retrieved {len(featured_products)} featured products")
                    else:
                        self.log_result("GET /products?featured=true", False, f"Some non-featured products in results")
                else:
                    self.log_result("GET /products?featured=true", False, "Invalid response format")
            else:
                self.log_result("GET /products?featured=true", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("GET /products?featured=true", False, f"Error: {str(e)}")
        
        # Test GET /api/products?on_sale=true
        try:
            response = self.session.get(f"{BACKEND_URL}/products?on_sale=true")
            if response.status_code == 200:
                sale_products = response.json()
                if isinstance(sale_products, list):
                    sale_count = len([p for p in sale_products if p.get("is_on_sale")])
                    if sale_count == len(sale_products):
                        self.log_result("GET /products?on_sale=true", True, f"Retrieved {len(sale_products)} sale products")
                    else:
                        self.log_result("GET /products?on_sale=true", False, f"Some non-sale products in results")
                else:
                    self.log_result("GET /products?on_sale=true", False, "Invalid response format")
            else:
                self.log_result("GET /products?on_sale=true", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("GET /products?on_sale=true", False, f"Error: {str(e)}")
        
        # Test GET /api/products?category_id=cat_dairy
        try:
            response = self.session.get(f"{BACKEND_URL}/products?category_id=cat_dairy")
            if response.status_code == 200:
                dairy_products = response.json()
                if isinstance(dairy_products, list):
                    dairy_count = len([p for p in dairy_products if p.get("category_id") == "cat_dairy"])
                    if dairy_count == len(dairy_products):
                        self.log_result("GET /products?category_id=cat_dairy", True, f"Retrieved {len(dairy_products)} dairy products")
                    else:
                        self.log_result("GET /products?category_id=cat_dairy", False, f"Some non-dairy products in results")
                else:
                    self.log_result("GET /products?category_id=cat_dairy", False, "Invalid response format")
            else:
                self.log_result("GET /products?category_id=cat_dairy", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("GET /products?category_id=cat_dairy", False, f"Error: {str(e)}")
        
        # Test GET /api/products?search=domates
        try:
            response = self.session.get(f"{BACKEND_URL}/products?search=domates")
            if response.status_code == 200:
                search_products = response.json()
                if isinstance(search_products, list):
                    # Check if results contain tomato products
                    tomato_found = any("domates" in p.get("name_tr", "").lower() or "tomato" in p.get("name", "").lower() 
                                     for p in search_products)
                    if tomato_found:
                        self.log_result("GET /products?search=domates", True, f"Found {len(search_products)} products matching 'domates'")
                    else:
                        self.log_result("GET /products?search=domates", False, f"No tomato products found in search results")
                else:
                    self.log_result("GET /products?search=domates", False, "Invalid response format")
            else:
                self.log_result("GET /products?search=domates", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("GET /products?search=domates", False, f"Error: {str(e)}")
        
        # Test GET /api/products/prod_1
        try:
            response = self.session.get(f"{BACKEND_URL}/products/prod_1")
            if response.status_code == 200:
                product = response.json()
                if product.get("id") == "prod_1" and product.get("name"):
                    self.log_result("GET /products/prod_1", True, f"Retrieved product: {product['name']}")
                else:
                    self.log_result("GET /products/prod_1", False, f"Invalid product data: {product}")
            else:
                self.log_result("GET /products/prod_1", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("GET /products/prod_1", False, f"Error: {str(e)}")
    
    def test_banners_api(self):
        """Test Banners API"""
        print("\n=== Testing Banners API ===")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/banners")
            if response.status_code == 200:
                banners = response.json()
                if isinstance(banners, list) and len(banners) > 0:
                    self.log_result("GET /banners", True, f"Retrieved {len(banners)} banners")
                else:
                    self.log_result("GET /banners", False, f"No banners returned or invalid format")
            else:
                self.log_result("GET /banners", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("GET /banners", False, f"Error: {str(e)}")
    
    def test_cart_api(self):
        """Test Cart API endpoints"""
        print("\n=== Testing Cart API ===")
        
        # Test GET /api/cart/{session_id} - empty cart
        try:
            response = self.session.get(f"{BACKEND_URL}/cart/{self.test_session_id}")
            if response.status_code == 200:
                cart = response.json()
                if cart.get("session_id") == self.test_session_id and isinstance(cart.get("items"), list):
                    self.log_result("GET /cart/{session_id} - empty", True, f"Retrieved empty cart for session {self.test_session_id}")
                else:
                    self.log_result("GET /cart/{session_id} - empty", False, f"Invalid cart structure: {cart}")
            else:
                self.log_result("GET /cart/{session_id} - empty", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("GET /cart/{session_id} - empty", False, f"Error: {str(e)}")
        
        # Test POST /api/cart/{session_id}/add
        try:
            add_data = {"product_id": "prod_1", "quantity": 2}
            response = self.session.post(f"{BACKEND_URL}/cart/{self.test_session_id}/add", 
                                       json=add_data)
            if response.status_code == 200:
                result = response.json()
                if "message" in result and "cart" in result:
                    self.log_result("POST /cart/{session_id}/add", True, f"Added product to cart: {result['message']}")
                else:
                    self.log_result("POST /cart/{session_id}/add", False, f"Invalid response: {result}")
            else:
                self.log_result("POST /cart/{session_id}/add", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("POST /cart/{session_id}/add", False, f"Error: {str(e)}")
        
        # Test GET /api/cart/{session_id} - with items
        try:
            response = self.session.get(f"{BACKEND_URL}/cart/{self.test_session_id}")
            if response.status_code == 200:
                cart = response.json()
                if len(cart.get("items", [])) > 0:
                    item = cart["items"][0]
                    if item.get("product_id") == "prod_1" and item.get("quantity") == 2:
                        self.log_result("GET /cart/{session_id} - with items", True, f"Cart contains added item: {item}")
                    else:
                        self.log_result("GET /cart/{session_id} - with items", False, f"Item not found or incorrect: {cart}")
                else:
                    self.log_result("GET /cart/{session_id} - with items", False, f"Cart is empty after adding item")
            else:
                self.log_result("GET /cart/{session_id} - with items", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("GET /cart/{session_id} - with items", False, f"Error: {str(e)}")
        
        # Test PUT /api/cart/{session_id}/update
        try:
            update_data = {"product_id": "prod_1", "quantity": 5}
            response = self.session.put(f"{BACKEND_URL}/cart/{self.test_session_id}/update", 
                                      json=update_data)
            if response.status_code == 200:
                result = response.json()
                if "message" in result:
                    self.log_result("PUT /cart/{session_id}/update", True, f"Updated cart item: {result['message']}")
                else:
                    self.log_result("PUT /cart/{session_id}/update", False, f"Invalid response: {result}")
            else:
                self.log_result("PUT /cart/{session_id}/update", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("PUT /cart/{session_id}/update", False, f"Error: {str(e)}")
        
        # Test DELETE /api/cart/{session_id}/remove/{product_id}
        try:
            response = self.session.delete(f"{BACKEND_URL}/cart/{self.test_session_id}/remove/prod_1")
            if response.status_code == 200:
                result = response.json()
                if "message" in result:
                    self.log_result("DELETE /cart/{session_id}/remove/{product_id}", True, f"Removed item: {result['message']}")
                else:
                    self.log_result("DELETE /cart/{session_id}/remove/{product_id}", False, f"Invalid response: {result}")
            else:
                self.log_result("DELETE /cart/{session_id}/remove/{product_id}", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("DELETE /cart/{session_id}/remove/{product_id}", False, f"Error: {str(e)}")
        
        # Test DELETE /api/cart/{session_id}/clear
        try:
            response = self.session.delete(f"{BACKEND_URL}/cart/{self.test_session_id}/clear")
            if response.status_code == 200:
                result = response.json()
                if "message" in result:
                    self.log_result("DELETE /cart/{session_id}/clear", True, f"Cleared cart: {result['message']}")
                else:
                    self.log_result("DELETE /cart/{session_id}/clear", False, f"Invalid response: {result}")
            else:
                self.log_result("DELETE /cart/{session_id}/clear", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("DELETE /cart/{session_id}/clear", False, f"Error: {str(e)}")
    
    def test_favorites_api(self):
        """Test Favorites API endpoints"""
        print("\n=== Testing Favorites API ===")
        
        # Test GET /api/favorites/{session_id} - empty
        try:
            response = self.session.get(f"{BACKEND_URL}/favorites/{self.test_session_id}")
            if response.status_code == 200:
                favorites = response.json()
                if favorites.get("session_id") == self.test_session_id and isinstance(favorites.get("product_ids"), list):
                    self.log_result("GET /favorites/{session_id} - empty", True, f"Retrieved empty favorites for session {self.test_session_id}")
                else:
                    self.log_result("GET /favorites/{session_id} - empty", False, f"Invalid favorites structure: {favorites}")
            else:
                self.log_result("GET /favorites/{session_id} - empty", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("GET /favorites/{session_id} - empty", False, f"Error: {str(e)}")
        
        # Test POST /api/favorites/{session_id}/toggle/{product_id} - add
        try:
            response = self.session.post(f"{BACKEND_URL}/favorites/{self.test_session_id}/toggle/prod_1")
            if response.status_code == 200:
                result = response.json()
                if result.get("is_favorite") == True:
                    self.log_result("POST /favorites/{session_id}/toggle/{product_id} - add", True, f"Added to favorites: {result['message']}")
                else:
                    self.log_result("POST /favorites/{session_id}/toggle/{product_id} - add", False, f"Product not added to favorites: {result}")
            else:
                self.log_result("POST /favorites/{session_id}/toggle/{product_id} - add", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("POST /favorites/{session_id}/toggle/{product_id} - add", False, f"Error: {str(e)}")
        
        # Test GET /api/favorites/{session_id} - with items
        try:
            response = self.session.get(f"{BACKEND_URL}/favorites/{self.test_session_id}")
            if response.status_code == 200:
                favorites = response.json()
                if "prod_1" in favorites.get("product_ids", []):
                    self.log_result("GET /favorites/{session_id} - with items", True, f"Favorites contains added product")
                else:
                    self.log_result("GET /favorites/{session_id} - with items", False, f"Product not found in favorites: {favorites}")
            else:
                self.log_result("GET /favorites/{session_id} - with items", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("GET /favorites/{session_id} - with items", False, f"Error: {str(e)}")
        
        # Test POST /api/favorites/{session_id}/toggle/{product_id} - remove
        try:
            response = self.session.post(f"{BACKEND_URL}/favorites/{self.test_session_id}/toggle/prod_1")
            if response.status_code == 200:
                result = response.json()
                if result.get("is_favorite") == False:
                    self.log_result("POST /favorites/{session_id}/toggle/{product_id} - remove", True, f"Removed from favorites: {result['message']}")
                else:
                    self.log_result("POST /favorites/{session_id}/toggle/{product_id} - remove", False, f"Product not removed from favorites: {result}")
            else:
                self.log_result("POST /favorites/{session_id}/toggle/{product_id} - remove", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("POST /favorites/{session_id}/toggle/{product_id} - remove", False, f"Error: {str(e)}")
    
    def test_orders_api(self):
        """Test Orders API endpoints"""
        print("\n=== Testing Orders API ===")
        
        # First add items to cart for test_session_456
        try:
            add_data = {"product_id": "prod_1", "quantity": 2}
            response = self.session.post(f"{BACKEND_URL}/cart/{self.test_session_id_2}/add", 
                                       json=add_data)
            if response.status_code == 200:
                self.log_result("Setup cart for order", True, "Added items to cart for order testing")
            else:
                self.log_result("Setup cart for order", False, f"Failed to add items to cart: {response.status_code}")
                return
        except Exception as e:
            self.log_result("Setup cart for order", False, f"Error setting up cart: {str(e)}")
            return
        
        # Test POST /api/orders - create order
        try:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            order_data = {
                "session_id": self.test_session_id_2,
                "delivery_address": {
                    "full_name": "Test User",
                    "phone": "05551234567",
                    "address": "Test Street 123",
                    "city": "Istanbul",
                    "district": "Kadikoy",
                    "notes": "Test note"
                },
                "delivery_date": tomorrow,
                "delivery_time_slot": "09:00 - 12:00",
                "payment_method": "cash_on_delivery"
            }
            
            response = self.session.post(f"{BACKEND_URL}/orders", json=order_data)
            if response.status_code == 200:
                order = response.json()
                if order.get("id") and order.get("session_id") == self.test_session_id_2:
                    self.order_id = order["id"]
                    self.log_result("POST /orders", True, f"Created order: {order['id']}")
                else:
                    self.log_result("POST /orders", False, f"Invalid order response: {order}")
            else:
                self.log_result("POST /orders", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("POST /orders", False, f"Error: {str(e)}")
        
        # Test GET /api/orders/{session_id}
        try:
            response = self.session.get(f"{BACKEND_URL}/orders/{self.test_session_id_2}")
            if response.status_code == 200:
                orders = response.json()
                if isinstance(orders, list) and len(orders) > 0:
                    self.log_result("GET /orders/{session_id}", True, f"Retrieved {len(orders)} orders")
                else:
                    self.log_result("GET /orders/{session_id}", False, f"No orders found or invalid format")
            else:
                self.log_result("GET /orders/{session_id}", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("GET /orders/{session_id}", False, f"Error: {str(e)}")
        
        # Test GET /api/orders/{session_id}/{order_id}
        if hasattr(self, 'order_id'):
            try:
                response = self.session.get(f"{BACKEND_URL}/orders/{self.test_session_id_2}/{self.order_id}")
                if response.status_code == 200:
                    order = response.json()
                    if order.get("id") == self.order_id:
                        self.log_result("GET /orders/{session_id}/{order_id}", True, f"Retrieved order detail: {order['id']}")
                    else:
                        self.log_result("GET /orders/{session_id}/{order_id}", False, f"Invalid order detail: {order}")
                else:
                    self.log_result("GET /orders/{session_id}/{order_id}", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("GET /orders/{session_id}/{order_id}", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Migros Sanal Market Backend API Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Test API connectivity first
        if not self.test_api_root():
            print("\n❌ API is not accessible. Stopping tests.")
            return False
        
        # Run all test suites
        self.test_categories_api()
        self.test_products_api()
        self.test_banners_api()
        self.test_cart_api()
        self.test_favorites_api()
        self.test_orders_api()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = len([r for r in self.results if r["success"]])
        failed = len([r for r in self.results if not r["success"]])
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        return failed == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)