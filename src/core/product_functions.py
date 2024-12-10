"""Product management functions"""
import logging
import tkinter as messagebox
import traceback
from tkinter import *

from firebase_admin import firestore

from .firebase_utils import check_firebase_connection

cart_list = []



def fetch_products():
    """Fetch products with connection validation"""
    try:
        if not check_firebase_connection():
            raise ConnectionError("Firebase connection failed")
            
        db = firestore.client()
        products_ref = db.collection('All-Products').document('Products-List')
        doc = products_ref.get()
        
        if not doc.exists:
            logging.warning("Products document not found")
            return [{"Name": product["Name"], "Price": product["Price"], "QTY": product["QTY"]} for product in products]
            
        products = doc.to_dict().get('Products', [])
        
        if products is None:
            logging.warning("No products found in the document")
            return []  # Return an empty list if no products are found
            
        logging.info(f"Successfully fetched {len(products)} products")
        return products
        
    except Exception as e:
        logging.error(f"Error fetching products: {str(e)}")
        traceback.print_exc()
        return []
    
def update_product_quantity():
    """Update product quantities in Firestore after bill generation"""
    try:
        # Get current products from Firestore
        db = firestore.client()
        products_ref = db.collection("All-Products").document("Products-List")
        doc = products_ref.get()
        products = doc.to_dict().get("Products", [])
            
            # Update quantities for products in cart
        for cart_item in cart_list:
            pid = cart_item[0]
            sold_qty = int(cart_item[3])
                
                # Find and update the product quantity
            for product in products:
                if product["PID"] == pid:
                    current_qty = int(product["QTY"])
                    if current_qty >= sold_qty:
                        product["QTY"] = str(current_qty - sold_qty)
                    else:
                        messagebox.showerror("Error", f"Not enough stock for product {product['Name']}")
                        return False
                    break
            
            # Update Firestore with new quantities
        products_ref.set({"Products": products})
            
        return True
            
    except Exception as e:
        messagebox.showerror("Error", f"Error updating stock: {str(e)}")
        return False

def create_product(name, pid, price, qty):
    """Create product with validation and error handling"""
    try:    
        if not check_firebase_connection():
            raise ConnectionError("Firebase connection failed")
            
        # Validate inputs
        if float(price) <= 0:
            raise ValueError("Price must be greater than 0")
        if int(qty) < 0:
            raise ValueError("Quantity cannot be negative")
            
        db = firestore.client()
        products_ref = db.collection('All-Products').document('Products-List')
        
        # Check if product ID already exists
        existing_products = fetch_products()
        if any(p.get('PID') == pid for p in existing_products):
            raise ValueError(f"Product with ID {pid} already exists")
            
        product_data = {
            'Name': name,
            'PID': pid,
            'Price': float(price),
            'QTY': int(qty)
        }
        
        # Add to existing products
        existing_products.append(product_data)
        products_ref.set({'Products': existing_products}, merge=True)
        
        logging.info(f"Successfully created product: {name} (ID: {pid})")
        return True
        
    except ValueError as ve:
        logging.error(f"Validation error in create_product: {str(ve)}")
        raise
    except Exception as e:
        logging.error(f"Error creating product: {str(e)}")
        traceback.print_exc()
        return False

def modify_product( pid, name, price, qty):
    """Update product details in Firestore."""
    try:
        db = firestore.client()
        # Reference to the products document
        products_ref = db.collection('All-Products').document('Products-List')
        doc = products_ref.get()
        
        if doc.exists:
            products = doc.to_dict().get('Products', [])
            
            # Find the product to update
            for product in products:
                if product['PID'] == pid:
                    product['Name'] = name
                    product['Price'] = price
                    product['QTY'] = qty
                    break
            
            # Update Firestore with modified products list
            products_ref.set({"Products": products})
            return True
        else:
            messagebox.showerror("Error", "Product list not found in Firestore.")
            return False
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update product: {str(e)}")
        return False
