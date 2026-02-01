import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json

BASE_URL = "https://fast-ecomm-4.onrender.com" or "http://localhost:8000"

st.set_page_config(
    page_title="E-Commerce Admin",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .product-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #f9f9f9;
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("🛍️ E-Commerce Admin")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "View Products", "Add Product", "Search & Filter", "Delete Product", "Update Product"]
)

def get_all_products():
    try:
        all_products = []
        offset = 0
        limit = 100
        
        while True:
            response = requests.get(
                f"{BASE_URL}/products?limit={limit}&offset={offset}", 
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                all_products.extend(items)
                
                if len(items) < limit:
                    break
                
                offset += limit
            else:
                error_detail = response.json().get("detail", "Unknown error")
                st.error(f"API Error: {response.status_code} - {error_detail}")
                return []
        
        return all_products
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching products: {e}")
        return []
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return []

def check_health():
    try:
        response = requests.get(f"{BASE_URL}/health")
        return response.status_code == 200
    except:
        return False

if not check_health():
    st.error("❌ FastAPI server is not running! Please start it first.")
    st.info("Run: `uvicorn app.main:app --reload`")
else:
    st.success("✅ API Connection Established")

if page == "Dashboard":
    st.title("📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    products = get_all_products()
    
    with col1:
        st.metric("Total Products", len(products))
    
    with col2:
        if products:
            avg_price = sum(p.get("price", 0) for p in products) / len(products)
            st.metric("Average Price", f"₹{avg_price:.2f}")
        else:
            st.metric("Average Price", "N/A")
    
    with col3:
        if products:
            max_price = max(p.get("price", 0) for p in products)
            st.metric("Max Price", f"₹{max_price:.2f}")
        else:
            st.metric("Max Price", "N/A")
    
    st.divider()
    
    if products:
        st.subheader("📈 Price Distribution")
        prices = [p.get("price", 0) for p in products]
        st.bar_chart({"Price": prices})
    else:
        st.warning("No products available for dashboard")

elif page == "View Products":
    st.title("📦 All Products")
    
    products = get_all_products()
    
    if products:
        df = pd.DataFrame(products)
        
        display_cols = [col for col in ["name", "price", "stock", "sku", "category", "brand"] if col in df.columns]
        
        st.dataframe(
            df[display_cols],
            use_container_width=True,
            height=600
        )
        
        st.success(f"✅ Showing {len(products)} products")
    else:
        st.error("❌ No products found. Check that your FastAPI server is running and has products loaded.")

elif page == "Add Product":
    st.title("➕ Add New Product")
    
    with st.form("add_product_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Product Name*", help="Product name (required)")
            price = st.number_input("Price*", min_value=0.0, step=0.01, help="Product price in ₹")
            stock = st.number_input("Stock Quantity*", min_value=0, step=1, help="Available quantity")
        
        with col2:
            sku = st.text_input("SKU*", help="Stock Keeping Unit (unique identifier)")
            description = st.text_area("Description", help="Product description")
        
        st.subheader("Seller Information")
        seller_col1, seller_col2 = st.columns(2)
        
        with seller_col1:
            seller_name = st.text_input("Seller Name")
            seller_email = st.text_input("Seller Email")
        
        with seller_col2:
            seller_website = st.text_input("Seller Website", placeholder="https://example.com")
            seller_id = st.text_input("Seller ID (UUID)")
        
        submit = st.form_submit_button("Add Product", use_container_width=True)
        
        if submit:
            if not all([name, sku, price, stock]):
                st.error("Please fill in all required fields (*)")
            else:
                product_data = {
                    "name": name,
                    "sku": sku,
                    "price": float(price),
                    "stock": int(stock),
                    "description": description,
                }
                
                if seller_name and seller_email:
                    product_data["seller"] = {
                        "seller_id": seller_id or "00000000-0000-0000-0000-000000000000",
                        "name": seller_name,
                        "email": seller_email,
                        "website": seller_website or "https://example.com"
                    }
                
                try:
                    response = requests.post(f"{BASE_URL}/products", json=product_data)
                    if response.status_code == 201:
                        st.success("✅ Product added successfully!")
                        st.cache_data.clear()
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Request failed: {e}")

elif page == "Search & Filter":
    st.title("🔍 Search & Filter Products")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_name = st.text_input("Search by name")
    
    with col2:
        sort_price = st.checkbox("Sort by price")
    
    with col3:
        if sort_price:
            order = st.radio("Sort order", ["Ascending", "Descending"], horizontal=True)
            order_param = "asc" if order == "Ascending" else "desc"
        else:
            order_param = "asc"
    
    limit = st.slider("Number of products", 1, 100, 10)
    
    params = {"limit": limit}
    if search_name:
        params["name"] = search_name
    if sort_price:
        params["sort_by_price"] = True
        params["order"] = order_param
    
    try:
        response = requests.get(f"{BASE_URL}/products", params=params)
        if response.status_code == 200:
            data = response.json()
            products = data.get("items", [])
            total = data.get("total", 0)
            
            st.info(f"Found {total} product(s) - Showing {len(products)}")
            
            if products:
                df = pd.DataFrame(products)
                display_cols = [col for col in ["name", "price", "stock", "sku"] if col in df.columns]
                st.dataframe(df[display_cols], use_container_width=True)
            else:
                st.warning("No products found matching your criteria")
        else:
            st.error(response.json().get("detail", "Error fetching products"))
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")

elif page == "Delete Product":
    st.title("🗑️ Delete Product")
    
    products = get_all_products()
    
    if products:
        product_names = {p["id"]: f"{p.get('name', 'Unknown')} (ID: {p['id'][:8]}...)" for p in products}
        
        selected_id = st.selectbox(
            "Select product to delete",
            options=list(product_names.keys()),
            format_func=lambda x: product_names[x]
        )
        
        if selected_id:
            product = next(p for p in products if p["id"] == selected_id)
            
            st.warning("⚠️ Delete confirmation")
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                st.write(f"**Name:** {product.get('name')}")
            with col2:
                st.write(f"**SKU:** {product.get('sku')}")
            with col3:
                st.write(f"**Price:** ₹{product.get('price', 0)}")
            
            if st.button("🗑️ Confirm Delete", type="secondary"):
                try:
                    response = requests.delete(f"{BASE_URL}/products/{selected_id}")
                    if response.status_code == 200:
                        st.success("✅ Product deleted successfully!")
                        st.cache_data.clear()
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Request failed: {e}")
    else:
        st.warning("No products available to delete")

elif page == "Update Product":
    st.title("✏️ Update Product")
    
    products = get_all_products()
    
    if products:
        product_names = {p["id"]: f"{p.get('name', 'Unknown')} (ID: {p['id'][:8]}...)" for p in products}
        
        selected_id = st.selectbox(
            "Select product to update",
            options=list(product_names.keys()),
            format_func=lambda x: product_names[x]
        )
        
        if selected_id:
            current_product = next(p for p in products if p["id"] == selected_id)
            
            st.subheader("Current Product Details")
            st.json(current_product)
            
            st.divider()
            st.subheader("Update Fields")
            
            with st.form("update_product_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input(
                        "Product Name",
                        value=current_product.get("name", ""),
                        help="Leave empty to keep unchanged"
                    )
                    new_price = st.number_input(
                        "Price",
                        value=float(current_product.get("price", 0)),
                        min_value=0.0,
                        step=0.01
                    )
                
                with col2:
                    new_stock = st.number_input(
                        "Stock",
                        value=int(current_product.get("stock", 0)),
                        min_value=0,
                        step=1
                    )
                    new_description = st.text_area(
                        "Description",
                        value=current_product.get("description", "")
                    )
                
                submit = st.form_submit_button("Update Product", use_container_width=True)
                
                if submit:
                    update_data = {}
                    
                    if new_name and new_name != current_product.get("name"):
                        update_data["name"] = new_name
                    if new_price != current_product.get("price"):
                        update_data["price"] = new_price
                    if new_stock != current_product.get("stock"):
                        update_data["stock"] = new_stock
                    if new_description != current_product.get("description"):
                        update_data["description"] = new_description
                    
                    if update_data is not None and len(update_data) > 0:
                        try:
                            response = requests.patch(
                                f"{BASE_URL}/products/{selected_id}",
                                json=update_data
                            )
                            if response.status_code == 200:
                                st.success("✅ Product updated successfully!")
                                st.cache_data.clear()
                            else:
                                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                        except requests.exceptions.RequestException as e:
                            st.error(f"Request failed: {e}")
                    else:
                        st.info("No changes made")
    else:
        st.warning("No products available to update")

st.divider()
st.markdown("""
---
**E-Commerce Admin Panel** | Built with Streamlit + FastAPI
""")
