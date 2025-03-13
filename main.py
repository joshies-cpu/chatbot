from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import uvicorn
import sqlite3

app = FastAPI()

# Expanded Product Database
products = [
    {"id": 1, "name": "Organic Apple", "category": "Fruits", "brand": "Farm Fresh", "price": 5},
    {"id": 2, "name": "Brown Rice", "category": "Grains", "brand": "Healthy Farm", "price": 10},
    {"id": 3, "name": "Almond Milk", "category": "Dairy", "brand": "Vegan Life", "price": 7},
    {"id": 4, "name": "Banana", "category": "Fruits", "brand": "Tropical Farms", "price": 3},
    {"id": 5, "name": "Mango", "category": "Fruits", "brand": "Golden Harvest", "price": 8},
    {"id": 6, "name": "Blueberries", "category": "Fruits", "brand": "Berry Bliss", "price": 12},
]

# Store User Search History (Temporary In-Memory)
USER_HISTORY = {}

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect("chatbot.db")
    conn.row_factory = sqlite3.Row
    return conn

# Product Search Endpoint
@app.get("/search")
def search_products(
    user_id: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = None
):
    filtered_products = [p for p in products]

    if category:
        filtered_products = [p for p in filtered_products if p["category"].lower() == category.lower()]
    if brand:
        filtered_products = [p for p in filtered_products if p["brand"].lower() == brand.lower()]
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] >= min_price]
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] <= max_price]

    if sort_by == "price_low_to_high":
        filtered_products.sort(key=lambda x: x["price"])
    elif sort_by == "price_high_to_low":
        filtered_products.sort(key=lambda x: x["price"], reverse=True)

    if not filtered_products:
        return {"message": "No products found matching your criteria."}

    if user_id:
        USER_HISTORY.setdefault(user_id, {"searches": []})
        USER_HISTORY[user_id]["searches"].append({"category": category, "brand": brand})

    return {"products": filtered_products}

# New Product Details Endpoint
@app.get("/product_details")
def product_details(product_id: int):
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        return {"product": product}
    raise HTTPException(status_code=404, detail="Product not found")

# New Order Status Endpoint
@app.get("/order_status")
def order_status(order_id: int):
    # Placeholder logic for demonstration
    sample_orders = {
        101: {"status": "Shipped", "delivery_date": "March 15, 2025"},
        102: {"status": "Processing", "delivery_date": "March 18, 2025"},
        103: {"status": "Delivered", "delivery_date": "March 10, 2025"},
    }

    order_info = sample_orders.get(order_id)
    if order_info:
        return order_info
    raise HTTPException(status_code=404, detail="Order not found")

# Recommendation System Setup
product_descriptions = [
    {"id": 1, "description": "Fresh organic apples from farm"},
    {"id": 2, "description": "Healthy brown rice, good for diet"},
    {"id": 3, "description": "Plant-based almond milk, dairy-free"},
    {"id": 4, "description": "Tropical bananas rich in potassium"},
    {"id": 5, "description": "Sweet and juicy mangoes"},
    {"id": 6, "description": "Fresh blueberries full of antioxidants"},
]

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform([p["description"] for p in product_descriptions])

@app.get("/recommend")
def recommend_products(user_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get user preferences
    cursor.execute("SELECT category, brand, min_price, max_price FROM user_preferences WHERE user_id = ?", (user_id,))
    preferences = cursor.fetchall()

    if not preferences:
        return {"message": "No preferences found. Try searching for products first!"}

    # Get purchase history
    cursor.execute("SELECT product_name FROM purchase_history WHERE user_id = ?", (user_id,))
    purchase_history = [row["product_name"] for row in cursor.fetchall()]

    # Extract most recent preferences
    category = preferences[-1]["category"]
    brand = preferences[-1]["brand"]
    min_price = preferences[-1]["min_price"]
    max_price = preferences[-1]["max_price"]

    # Filter products based on preferences
    filtered_products = [p for p in products]
    if category:
        filtered_products = [p for p in filtered_products if p["category"].lower() == category.lower()]
    if brand:
        filtered_products = [p for p in filtered_products if p["brand"].lower() == brand.lower()]
    if min_price:
        filtered_products = [p for p in filtered_products if p["price"] >= min_price]
    if max_price:
        filtered_products = [p for p in filtered_products if p["price"] <= max_price]

    # Exclude products already purchased
    filtered_products = [p for p in filtered_products if p["name"] not in purchase_history]

    if not filtered_products:
        return {"message": "No recommendations available based on your preferences."}

    # Use TF-IDF and cosine similarity for content-based filtering
    product_descriptions_filtered = [
        {"id": p["id"], "description": f"{p['name']} {p['category']} {p['brand']}"}
        for p in filtered_products
    ]
    tfidf_matrix_filtered = vectorizer.transform([p["description"] for p in product_descriptions_filtered])

    first_product = product_descriptions_filtered[0]
    index = next((i for i, p in enumerate(product_descriptions_filtered) if p["id"] == first_product["id"]), None)

    if index is None:
        return {"message": "Product not found in recommendation dataset."}

    # Calculate similarities
    similarities = cosine_similarity(tfidf_matrix_filtered[index], tfidf_matrix_filtered).flatten()
    similar_indices = similarities.argsort()[::-1][1:3]  # Top 2 similar products
    recommended_products = [filtered_products[i] for i in similar_indices]

    return {"recommended_products": recommended_products}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
