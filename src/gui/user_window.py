"""
User window GUI module for normal users.
"""
# Standard library imports
import os
import csv
import glob
import time
import shutil
import tempfile
import traceback
from datetime import datetime

import traceback


# Third-party imports
from firebase_admin import firestore
import pandas as pd


# Tkinter imports
# import tkinter 
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

# Logging imports
import logging
import logging.handlers
import gc
 
from src.core.admin_functions import initialize_directories
from src.core.firebase_utils import connect_firebase, get_db_instance

class UserIMS:
    """
    User Interface for Inventory Management System.
    Handles product display, cart management, and billing operations.
    """
    def __init__(self, root):
        try:
            self.root = root
            self.root.title("Inventory Management System")
            # Set the window to full screen
            self.root.attributes('-fullscreen', True)  # Enable full screen
            # Optionally, remove window decorations
            # self.root.overrideredirect(True)  # Uncomment to remove title bar

            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            
            # Get directory paths from initialize_directories
            dirs = initialize_directories()
            if dirs:
                self.bills_dir = dirs['bills']
                self.csv_dir = dirs['csv']
                self.cache_dir = dirs['cache']
            
            # Clear cache directory on startup
            self.clear_cache()
            
            # Initialize all StringVar variables
            self.var_search = StringVar()
            self.var_searchtxt = StringVar()
            self.var_searchby = StringVar()
            self.var_pid = StringVar()
            self.var_name = StringVar()
            self.var_price = StringVar()
            self.var_qty = StringVar()
            self.var_stock = StringVar()
            self.var_cname = StringVar()
            self.var_contact = StringVar()
            
            # Calculator variables
            self.var_cal_input = StringVar()
            
            # Cart variables
            self.var_cart_pid = StringVar()
            self.var_cart_name = StringVar()
            self.var_cart_price = StringVar()
            self.var_cart_qty = StringVar()
            self.var_cart_stock = StringVar()
            
            # Initialize other variables
            self.bill_amnt = 0
            self.net_pay = 0
            self.discount = 0
            self.cart_list = []
            
            # Initialize database connection
            self.db = connect_firebase()
            
            # Add window closing handler
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

            self.running = True
            
            # Initialize widgets
            self.create_widgets()
            
            print("Application Start: User IMS initialized")
            
        except Exception as e:
            logging.error(f"Error initializing UserIMS: {str(e)}")
            messagebox.showerror("Error", "Failed to initialize application")

    def user_show(self):
        if self.db is None:
            return
        try:
            products_ref = self.db.collection("All-Products").document("Products-List")
            doc = products_ref.get()
            products = doc.to_dict().get("Products", [])  # get product list
            self.product_Table.delete(*self.product_Table.get_children())
            for product in products:
                self.product_Table.insert(
                    "",
                    END,
                    values=(
                        product["PID"],
                        product["Name"],
                        product["Price"],
                        product["QTY"],
                    ),
                )
        except Exception as e:
            messagebox.showerror("Firebase Error", f"Error fetching products: {e}")

    def user_search(self):
        if self.db is None:
            return
        try:
            search_term = self.var_search.get().lower()
            if not search_term:
                messagebox.showerror("Error", "Please enter a search term")
                return
            
            products_ref = self.db.collection("All-Products").document("Products-List")
            doc = products_ref.get()
            products = doc.to_dict().get("Products", [])
            
            # Clear existing items
            self.product_Table.delete(*self.product_Table.get_children())
            
            # Search and display matching products
            matching_products = [p for p in products if search_term in p["Name"].lower()]
            
            if matching_products:
                for p in matching_products:
                    self.product_Table.insert("", END, values=(
                        p["PID"],
                        p["Name"],
                        p["Price"],
                        p["QTY"]
                    ))
            else:
                messagebox.showinfo("Info", "No products found matching your search term")
                self.user_show()  # Show all products if no matches found
            
        except Exception as e:
            messagebox.showerror("Error", f"Error searching products: {e}")

    def user_get_data(self, ev):
    # """Fetch data when a product is selected from the product table."""
        try:
            f = self.product_Table.focus()
            content = self.product_Table.item(f)
            row = content["values"]
            # Fetch product details from Firestore
            products_ref = self.db.collection("All-Products").document("Products-List")
            doc = products_ref.get()
            products = doc.to_dict().get("Products", [])

            # Set values to input fields based on UI layout
            self.var_pid.set(row[0])  # PID
            self.var_name.set(row[1])  # Name
            self.var_price.set(row[2])  # Price Per Qty
            self.lbl_inStock.config(text=f"In Stock [{str(row[3])}]")
            self.var_qty.set("1")  # Set default quantity to 1

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def user_get_data_cart(self, ev):
        """Fetch data when a product is selected from the cart table."""
        try:
            selected_item = self.CartTable.selection()[0]
            values = self.CartTable.item(selected_item)['values']
            
            if values:
                self.var_pid.set(values[0])      # PID
                self.var_name.set(values[1])     # Name
                self.var_price.set(values[2])    # Price
                self.var_qty.set(values[3])      # Quantity
                
        except IndexError:
            pass  # No selection
        except Exception as e:
            print(f"Error getting cart data: {str(e)}")

    def user_add_update_cart(self):
        """Add or update items in the cart."""
        try:
            self.log_action("Cart Update", f"Product: {self.var_name.get()}, Qty: {self.var_qty.get()}")
            
            # Validate price is a positive number
            price = float(self.var_price.get().strip())
            if price <= 0:
                messagebox.showerror("Error", "Price must be greater than 0")
                return
            
            # Validate quantity is a positive integer
            qty = int(self.var_qty.get().strip())
            if qty <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0")
                return
            
            # Validate if a product is selected
            if not self.var_pid.get():
                messagebox.showerror("Error", "Please select a product from the list", parent=self.root)
                return

            # Validate if quantity is entered
            if not self.var_qty.get():
                messagebox.showerror("Error", "Quantity is required", parent=self.root)
                return

            # Get values from input fields
            pid = self.var_pid.get().strip()
            name = self.var_name.get().strip()
            price = float(self.var_price.get().strip())
            qty = int(self.var_qty.get().strip())

            # Validate quantity input
            if qty <= 0:
                messagebox.showerror("Error", "Invalid quantity. It must be greater than zero.", parent=self.root)
                return

            # Check available stock in Firestore
            products_ref = self.db.collection("All-Products").document("Products-List")
            doc = products_ref.get()
            products = doc.to_dict().get("Products", [])
            
            # Find current product stock
            current_stock = 0
            for product in products:
                if product["PID"] == pid:
                    current_stock = int(product["QTY"])
                    break
            
            # Check if requested quantity is available
            if qty > current_stock:
                messagebox.showerror("Error", f"Not enough stock! Available quantity: {current_stock}", parent=self.root)
                return

            # Calculate total price for the item
            total = price * qty

            # Check if the item already exists in the cart
            existing_item_index = next((idx for idx, item in enumerate(self.cart_list) if item[0] == pid), None)

            cart_item = [pid, name, price, qty, total]  # Format: [PID, Name, Price, Qty, Total]

            if existing_item_index is not None:
                # For updates, check if new total quantity exceeds stock
                other_cart_qty = sum(int(item[3]) for item in self.cart_list 
                                   if item[0] == pid and self.cart_list.index(item) != existing_item_index)
                if (qty + other_cart_qty) > current_stock:
                    messagebox.showerror("Error", 
                        f"Total quantity ({qty + other_cart_qty}) exceeds available stock ({current_stock})", 
                        parent=self.root)
                    return
                # Update existing item
                self.cart_list[existing_item_index] = cart_item
            else:
                # For new items, check if quantity exceeds stock
                cart_qty = sum(int(item[3]) for item in self.cart_list if item[0] == pid)
                if (qty + cart_qty) > current_stock:
                    messagebox.showerror("Error", 
                        f"Total quantity ({qty + cart_qty}) exceeds available stock ({current_stock})", 
                        parent=self.root)
                    return
                # Add new item
                self.cart_list.append(cart_item)

            # Update cart table display
            self.user_show_cart()
            
            # Update billing information
            self.user_bill_updates()
            
            # Clear input fields
            self.user_clear_cart_fields()

        except ValueError:
            messagebox.showerror("Error", "Invalid input! Please enter valid numeric values for quantity and price.", parent=self.root)
        except Exception as e:
            self.log_action("Error", f"Cart update failed: {str(e)}")
            logging.error(traceback.format_exc())
            messagebox.showerror("Error", f"Error adding to cart: {str(e)}", parent=self.root)
            print(f"Error details: {str(e)}")  # Debug print

    def user_show_cart(self):
        """Display items in the cart table and update cart title."""
        try:
            # Clear existing items in cart table
            self.CartTable.delete(*self.CartTable.get_children())
            
            # Insert all items from cart_list
            for item in self.cart_list:
                pid, name, price, qty, total = item
                self.CartTable.insert("", END, values=(pid, name, price, qty, total))
                
            # Update cart title with total products count
            total_products = len(self.cart_list)
            if hasattr(self, 'cartTitle'):
                self.cartTitle.config(text=f"🛒 Cart \t Total Products: [{total_products}]")
            
        except Exception as e:
            print(f"Error displaying cart: {str(e)}")

    def user_clear_cart_fields(self):
        """Clear input fields after adding/updating cart"""
        self.var_pid.set("")
        self.var_name.set("")
        self.var_price.set("")
        self.var_qty.set("")
        self.lbl_inStock.config(text="In Stock")

    def user_bill_updates(self):
        """Update billing information"""
        self.bill_amnt = 0
        self.net_pay = 0
        for item in self.cart_list:
            self.bill_amnt += float(item[2]) * int(item[3])  # price * quantity

        self.discount = (self.bill_amnt * 5) / 100  # 5% discount
        self.net_pay = self.bill_amnt - self.discount

        # Update labels with currency formatting
        self.lbl_amnt.config(text=f"Bill Amount\nRs. {self.bill_amnt:.2f}")
        self.lbl_discount.config(text=f"Discount\nRs. {self.discount:.2f}")
        self.lbl_net_pay.config(text=f"Net Pay\nRs. {self.net_pay:.2f}")
        self.cartTitle.config(text=f"🛒 Cart \t Total Products: [{len(self.cart_list)}]")

    def generate_bill(self):
        """Generate bill and display in text area"""
        try:
            # Validate cart and customer details
            if not self.cart_list:
                messagebox.showerror("Error", "Cart is empty")
                return
                
            if not self.var_cname.get() or not self.var_contact.get():
                messagebox.showerror("Error", "Customer details are required")
                return

            # Generate bill number
            self.bill_number = f"BILL{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Enable text area for writing
            self.txt_bill_area.config(state='normal')
            self.txt_bill_area.delete('1.0', END)
            
            try:
                # Add bill header
                self.bill_top(self.bill_number)
                
                # Add column headers
                self.bill_middle()
                
                # Prepare bill items for Firestore
                bill_items = []
                
                # Add cart items
                for item in self.cart_list:
                    name = item[1]
                    qty = item[3]
                    price = item[2]
                    total = item[4]
                        
                    # Add item to bill_items for Firestore
                    bill_items.append({
                        'pid': item[0],
                        'name': name,
                        'qty': qty,
                        'price': price,
                        'total': total
                    })
                    
                # Add bill footer
                self.bill_bottom()

                # Get Firestore references
                products_ref = self.db.collection("All-Products").document("Products-List")
                bills_ref = self.db.collection("Bills").document(self.bill_number)
                
                # Execute transaction
                transaction = self.db.transaction()
                
                @firestore.transactional
                def transaction_update(transaction, products_ref, bills_ref):
                    try:
                        # Get products document
                        products_doc = products_ref.get(transaction=transaction)
                        products = products_doc.to_dict().get("Products", [])
                        
                        # Update quantities
                        for item in self.cart_list:
                            pid = item[0]
                            qty = int(item[3])
                            
                            for product in products:
                                if product["PID"] == pid:
                                    current_qty = int(product["QTY"])
                                    if current_qty < qty:
                                        raise ValueError(f"Insufficient stock for {product['Name']}")
                                    product["QTY"] = str(current_qty - qty)
                                    break
                        
                        # Create new bill document in Firestore
                        new_bill_data = {
                            'bill_number': self.bill_number,
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'customer_name': self.var_cname.get(),
                            'customer_contact': self.var_contact.get(),
                            'items': bill_items,
                            'bill_amount': self.bill_amnt,
                            'discount': self.discount,
                            'net_pay': self.net_pay
                        }
                        
                        # Update products and create new bill document
                        transaction.update(products_ref, {"Products": products})
                        transaction.set(bills_ref, new_bill_data)  # Creates new document
                        
                        return True
                        
                    except Exception as e:
                        logging.error(f"Transaction failed: {str(e)}")
                        raise
                
                if transaction_update(transaction, products_ref, bills_ref):
                    messagebox.showinfo("Success", "Bill generated successfully\nClick Print to save the bill")
                
            except Exception as e:
                # If any error occurs during bill generation, clear the text area
                self.txt_bill_area.delete('1.0', END)
                raise e
                
            finally:
                # Disable text area after writing
                self.txt_bill_area.config(state='disabled')
            
        except Exception as e:
            self.txt_bill_area.config(state='normal')
            self.txt_bill_area.delete('1.0', END)
            self.txt_bill_area.config(state='disabled')
            logging.error(f"Failed to generate bill: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate bill: {str(e)}")

    def print_bill(self, bill_data=None):
        """Save the bill to file and CSV, and update stock quantities"""
        try:
            # Check if bill area is empty
            if not self.txt_bill_area.get('1.0', END).strip():
                self.log_action("Error", "Empty bill")
                messagebox.showerror("Error", "Please generate a bill first")
                return
            
            self.user_show

            # Get bill text and generate bill number
            bill_text = self.txt_bill_area.get('1.0', END)
            
            # Use provided bill number or generate new one
            if bill_data and 'bill_number' in bill_data:
                bill_no = bill_data['bill_number']
            else:
                bill_no = f"BILL{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Get directory paths
            dirs = initialize_directories()
            if not dirs:
                raise Exception("Failed to initialize directories")
            
            # Create bill path using the bills directory
            bill_path = dirs['bills'] / f"{bill_no}.txt"
            
            # Ensure directory exists
            bill_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write bill to file
            with open(bill_path, 'w') as f:
                f.write(bill_text)
            
            # Prepare data for CSV with improved formatting
            csv_data = {
                'Bill Number': bill_no,
                'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Customer Name': self.var_cname.get(),
                'Customer Contact': self.var_contact.get(),
                'Total Amount': f"Rs. {self.bill_amnt:,.2f}",
                'Discount': f"Rs. {self.discount:,.2f}",
                'Net Pay': f"Rs. {self.net_pay:,.2f}"
            }
            
            # Save to CSV
            self.save_to_csv(csv_data)
            
            # Update stock quantities
            if not self.update_stock_quantities():
                messagebox.showerror("Error", "Failed to update stock quantities.")
                return
            
            messagebox.showinfo("Success", "Bill has been saved successfully!")
            self.log_action("Print Bill", f"Bill saved: {bill_no}")
            
        except Exception as e:
            self.log_action("Error", f"Bill printing failed: {str(e)}")
            logging.error(traceback.format_exc())
            messagebox.showerror("Error", f"Error in saving bill: {str(e)}")

    def update_stock_quantities(self):
        """Update stock quantities in Firestore based on cart items"""
        try:
            db = get_db_instance()
            products_ref = db.collection("All-Products").document("Products-List")
            doc = products_ref.get()
            products = doc.to_dict().get("Products", [])

            # Update quantities based on cart items
            for item in self.cart_list:
                pid = item[0]  # Product ID
                qty = int(item[3])  # Quantity sold
                
                # Find the product and update its quantity
                for product in products:
                    if product["PID"] == pid:
                        current_qty = int(product["QTY"])
                        if current_qty >= qty:
                            product["QTY"] = str(current_qty - qty)  # Update quantity
                        else:
                            messagebox.showerror("Error", f"Not enough stock for product {product['Name']}")
                            return False
                        break
            
            # Save updated products back to Firestore
            products_ref.set({"Products": products})
            return True
                
        except Exception as e:
            logging.error(f"Failed to update stock quantities: {str(e)}")
            return False

    def bill_top(self, bill_number):
        # Enable text area for writing
        self.txt_bill_area.config(state='normal')
        
        # Get current date and time
        current_date = time.strftime("%d/%m/%Y")
        current_time = time.strftime("%H:%M:%S")
        
        bill_top_temp = f"""
\tXYZ-Inventory
\tPhone No. 98725*****, Gujarat-360001
{str("=" * 47)}
Bill No. {bill_number}
Customer Name: {self.var_cname.get()}
Ph no.: {self.var_contact.get()}
Date: {current_date}
Time: {current_time}
{str("=" * 47)}
Product Name\t\t\tQTY\tPrice
{str("=" * 47)}
"""
        self.txt_bill_area.delete("1.0", END)
        self.txt_bill_area.insert("1.0", bill_top_temp)
        
        # Disable text area after writing
        self.txt_bill_area.config(state='disabled')

    def bill_bottom(self):
        # Enable text area for writing
        self.txt_bill_area.config(state='normal')
        
        bill_bottom_temp = f"""
{str("=" * 47)}
Bill Amount\t\t\t\tRs.{self.bill_amnt}
Discount\t\t\t\tRs.{self.discount}
Net Pay\t\t\t\tRs.{self.net_pay}
{str("=" * 47)}\n
        """
        self.txt_bill_area.insert(END, bill_bottom_temp)
        
        # Disable text area after writing
        self.txt_bill_area.config(state='disabled')

    def bill_middle(self):
        # Enable text area for writing
        self.txt_bill_area.config(state='normal')
        
        for row in self.cart_list:
            name = row[1]
            qty = row[3]
            price = float(row[2]) * int(row[3])
            self.txt_bill_area.insert(END, f"\n {name}\t\t\t{qty}\tRs.{price}")
            
        # Disable text area after writing
        self.txt_bill_area.config(state='disabled')

    def update_system_clock(self):
        if not self.running:
            return
            
        current_time = time.strftime("%I:%M:%S %p")
        current_date = time.strftime("%d %B, %Y")
        self.clock_label.config(
                text=f"🗓️ {current_date}\n⏰ {current_time}")
        
        if self.running:
            self.clock_update_id = self.root.after(1000, self.update_system_clock)

    def create_widgets(self):
        # Updated Modern Theme Colors with a refined professional palette
        THEME = {
            "primary": "#1B3358",       # Deep navy blue (header)
            "secondary": "#325288",     # Medium navy blue
            "accent": "#CD4A4A",        # Refined red for attention/delete
            "surface": "#F7F7F7",       # Off-white background
            "text": "#2D3142",          # Dark charcoal text
            "input_bg": "#ffffff",      # Pure white input background
            "success": "#28A745",       # Forest green for success
            "warning": "#FFC107",       # Golden yellow for warnings
            "error": "#CD4A4A",         # Matching red for errors
            "info": "#4A90E2",          # Sky blue for information
            "card_bg": "#ffffff",       # White for cards
            "border": "#E2E8F0",        # Soft gray border
            "hover": "#FFB649",         # Golden hover states
            "calculator": {
                "num_btn": "#F0F4F8",   # Light blue-gray for number buttons
                "op_btn": "#325288",    # Navy for operator buttons
                "equal_btn": "#28A745", # Green for equals
                "clear_btn": "#CD4A4A"  # Red for clear
            }
        }

        # Custom Entry Style Function
        def create_modern_entry(parent, textvariable=None, width=180, height=30, readonly=False):
            # Create a frame for entry with a lighter border color
            entry_frame = Frame(
                parent, 
                bg="#bdc3c7",  # Lighter gray for border
                height=height+2,  # Reduced padding
                width=width+2    # Reduced padding
            )
            
            entry = Entry(
                entry_frame,
                textvariable=textvariable,
                font=("Segoe UI", 12),
                bg=THEME["input_bg"],
                fg=THEME["text"],
                relief="flat",
                bd=0
            )
            
            if readonly:
                entry.config(state='readonly', readonlybackground=THEME["input_bg"])
            
            # Place entry with 1px offset for subtle border
            entry.place(x=1, y=1, width=width-2, height=height-2)
            
            return entry_frame
        
    

        # Title Bar - Adjusted height and position
        self.header_frame = Frame(self.root, height=80, bg=THEME["primary"])
        self.header_frame.pack(side=TOP, fill=X)

        # Company Logo/Name
        self.logo_frame = Frame(self.header_frame, bg=THEME["primary"])
        self.logo_frame.pack(side=LEFT, padx=20)

        self.title_label = Label(
            self.logo_frame,
            text="🏪 Modern Inventory",
            font=("Helvetica", 24, "bold"),
            bg=THEME["primary"],
            fg="white"
        )
        self.title_label.pack(side=LEFT, pady=15)

        # Right side controls
        self.controls_frame = Frame(self.header_frame, bg=THEME["primary"])
        self.controls_frame.pack(side=RIGHT, padx=20)

        # Clock and Date
        self.datetime_frame = Frame(self.controls_frame, bg=THEME["primary"])
        self.datetime_frame.pack(side=LEFT, padx=20)

        self.clock_label = Label(
            self.datetime_frame,
            text="",
            font=("Helvetica", 12),
            bg=THEME["primary"],
            fg="#ecf0f1"
        )
        self.clock_label.pack()

        # Logout Button with hover effect
        self.logout_button = Button(
            self.controls_frame,
            text="Logout",
            font=("Helvetica", 12, "bold"),
            bg="#ff5252",
            fg="white",
            cursor="hand2",
            relief="flat",
            command=self.system_logout,  # Change from bind to command
            padx=20,
            pady=5
        )
        self.logout_button.pack(side=LEFT, pady=15)
        
        # Bind hover effects only
        self.logout_button.bind("<Enter>", lambda e: self.logout_button.config(bg="#ff1744"))
        self.logout_button.bind("<Leave>", lambda e: self.logout_button.config(bg="#ff5252"))
        # Remove the Button-1 binding since we're using command

        self.sub_header = Frame(self.root, bg=THEME["secondary"], height=40)
        self.sub_header.pack(side=TOP, fill=X)

        self.nav_label = Label(
            self.sub_header,
            text="📍 Billing Dashboard",
            font=("Helvetica", 12),
            bg=THEME["secondary"],
            fg="#ecf0f1"
        )
        self.nav_label.pack(side=LEFT, padx=20, pady=8)

        self.update_system_clock()
        # Footer - Changed to dark theme
        footer_frame = Frame(self.root, bg="#262626", height=45)  # Changed to dark gray
        footer_frame.pack(side=BOTTOM, fill=X, pady=(10, 0))  # Added padding for space adjustment
        
        footer_text = Label(
            footer_frame,
            text="IMS-Inventory Management System | Developed by: Meet Patel\nContact: work.meetpatel221@gmail.com",
            bg="#262626",  # Dark gray
            fg="white",
            font=("Segoe UI", 11)
        )
        footer_text.pack(pady=4)
        # Product Frame - Removed visible border
        ProductFrame1 = Frame(
            self.root,
            bg=THEME["card_bg"],
            relief="flat"  # Removed border
        )
        ProductFrame1.place(x=5, y=115, width=490, height=670)

        # Product Title - Updated styling
        pTitle = Label(
            ProductFrame1,
            text="📦 All Products",
            bg=THEME["primary"],
            font=("Segoe UI", 17, "bold"),
            fg="white",
            pady=10
        )
        pTitle.pack(side=TOP, fill=X)

        # Search Section - Adjusted spacing
        ProductFrame2 = Frame(ProductFrame1, bg=THEME["card_bg"])
        ProductFrame2.place(x=5, y=55, width=480, height=95)

        lbl_search = Label(
            ProductFrame2,
            text="🔍 Search Products",
            font=("Segoe UI", 15, "bold"),
            bg=THEME["card_bg"],
            fg=THEME["text"],
            pady=5
        )
        lbl_search.place(x=15, y=5)

        # Search Entry
        search_frame = create_modern_entry(
            ProductFrame2, 
            textvariable=self.var_search,
            width=330,
            height=38
        )
        search_frame.place(x=15, y=45)

        # Search and Show All buttons - Updated styling
        btn_search = Button(
            ProductFrame2,
            text="Search",
            command=self.user_search,
            cursor="hand2",
            font=("Segoe UI", 13, "bold"),
            bg=THEME["info"],
            fg="white",
            bd=0,
            relief="flat"
        )
        btn_search.place(x=355, y=45, width=110, height=38)

        btn_show_all = Button(
            ProductFrame2,
            text="Show All",
            command=self.user_show,
            cursor="hand2",
            font=("Segoe UI", 13, "bold"),
            bg=THEME["primary"],
            fg="white",
            bd=0,
            relief="flat"
        )
        btn_show_all.place(x=355, y=5, width=110, height=35)

        # Products Table - Adjusted position
        ProductFrame3 = Frame(ProductFrame1, bg=THEME["card_bg"])
        ProductFrame3.place(x=5, y=145, width=480, height=525)

        # Updated Treeview styling
        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            background=THEME["surface"],
            foreground=THEME["text"],
            fieldbackground=THEME["surface"],
            rowheight=35,
            font=("Segoe UI", 11)
        )
        scrolly = Scrollbar(ProductFrame3, orient=VERTICAL)
        self.product_Table = ttk.Treeview(
            ProductFrame3,
            columns=("pid", "name", "price", "qty"),
            yscrollcommand=scrolly.set,
            style="Custom.Treeview"
        )
        scrolly.pack(side=RIGHT, fill=Y)
        scrolly.config(command=self.product_Table.yview)

        self.product_Table.heading("pid", text="ID")
        self.product_Table.heading("name", text="Name")
        self.product_Table.heading("price", text="Price")
        self.product_Table.heading("qty", text="QTY")
        self.product_Table["show"] = "headings"
        self.product_Table.column("pid", width=50)
        self.product_Table.column("name", width=200)
        self.product_Table.column("price", width=100)
        self.product_Table.column("qty", width=100)
        self.product_Table.pack(fill=BOTH, expand=1)
        self.product_Table.bind("<ButtonRelease-1>", self.user_get_data)
        self.user_show()

        # Customer Frame - Adjusted height and spacing
        CustomerFrame = Frame(
            self.root,
            bg=THEME["surface"],
            relief="flat"
        )
        CustomerFrame.place(x=501, y=115, width=600, height=95)  # Increased height by 10px

        cTitle = Label(
            CustomerFrame,
            text="👤 Customer Details",
            bg=THEME["primary"],
            font=("Segoe UI", 14, "bold"),
            fg="white",
            pady=8  # Increased padding
        )
        cTitle.pack(side=TOP, fill=X)

        # Customer Details Fields
        self.var_cname = StringVar()
        self.var_contact = StringVar()

        lbl_name = Label(
            CustomerFrame,
            text="Name",
            font=("Segoe UI", 12, "bold"),
            bg=THEME["surface"]
        )
        lbl_name.place(x=5, y=50)  # Adjusted y position

        # Customer Name Entry - Increased width
        name_frame = create_modern_entry(
            CustomerFrame,
            textvariable=self.var_cname,
            width=200,  # Increased width
            height=28   # Increased height
        )
        name_frame.place(x=65, y=50)  # Adjusted position

        lbl_contact = Label(
            CustomerFrame,
            text="Contact",
            font=("Segoe UI", 12, "bold"),
            bg=THEME["surface"]
        )
        lbl_contact.place(x=280, y=50)  # Adjusted position

        # Customer Contact Entry - Increased width
        contact_frame = create_modern_entry(
            CustomerFrame,
            textvariable=self.var_contact,
            width=160,  # Increased width
            height=28   # Increased height
        )
        contact_frame.place(x=360, y=50)  # Adjusted position

        # Calculator and Cart Frame - Adjusted spacing
        # Cal_Cart_Frame = Frame(
        #     self.root,
        #     # bg=THEME["surface"],
        #     relief="flat"
        # )
        # Cal_Cart_Frame.place(x=501, y=215, width=600, height=450)  # Adjusted height
        Cal_Cart_Frame = Frame(self.root, relief="flat")
        Cal_Cart_Frame.place(x=501, y=215, width=600, height=450)

        # Calculator Title - Improved spacing
        cal_title = Label(
            self.root,
            text="🧮 Calculator",
            font=("Segoe UI", 14, "bold"), 
            bg=THEME["primary"],
            fg="white" # Added padding
        )
        cal_title.place(x=500, y=215, width=285, height=45)

        # Calculator Frame - Main content (removed dark background)
        Cal_Frame = Frame(Cal_Cart_Frame, bg=THEME["surface"])  # Changed from #1e272e to surface color
        Cal_Frame.place(x=0, y=45, width=282, height=410)

        # Calculator Entry Box - Using create_modern_entry for consistent style
        cal_entry_frame = create_modern_entry(
            Cal_Frame,
            textvariable=self.var_cal_input,
            width=272,    # Full width of calculator
            height=40     # Consistent height with other entries
        )
        cal_entry_frame.place(x=5, y=10)

        # Get the Entry widget from the frame to modify its properties
        cal_entry = cal_entry_frame.winfo_children()[0]  # Get the Entry widget
        cal_entry.config(
            font=("Segoe UI", 18, "bold"),  # Larger font for calculator
            justify="right",                 # Right-align text
            insertwidth=2                    # Wider cursor
        )

        # Calculator Buttons Frame - Removed dark background
        btn_frame = Frame(Cal_Frame, bg=THEME["surface"])  # Changed from #1e272e
        btn_frame.place(x=5, y=70, width=272, height=335)

        # Modern Calculator button style
        cal_btn_style = {
            "font": ("Segoe UI", 14, "bold"),
            "bd": 0,
            "relief": "flat",
            "cursor": "hand2",
            "width": 5,
            "height": 2,
            "borderwidth": 0,
            "highlightthickness": 0
        }

        # Button colors
        NUM_BTN_COLOR = "#34495e"      # Darker blue for numbers
        OP_BTN_COLOR = "#2980b9"       # Bright blue for operators
        EQUAL_BTN_COLOR = "#27ae60"    # Green for equals
        CLEAR_BTN_COLOR = "#c0392b"    # Red for clear

        # Calculator Buttons with updated colors and spacing
        btn_7 = Button(btn_frame, text='7', bg=THEME["calculator"]["num_btn"], fg=THEME["text"],
                      command=lambda: self.btn_click('7'), **cal_btn_style)
        btn_7.grid(row=0, column=0, padx=4, pady=4)

        btn_8 = Button(btn_frame, text='8', bg=THEME["calculator"]["num_btn"], fg=THEME["text"],
                      command=lambda: self.btn_click('8'), **cal_btn_style)
        btn_8.grid(row=0, column=1, padx=4, pady=4)

        btn_9 = Button(btn_frame, text='9', bg=THEME["calculator"]["num_btn"], fg=THEME["text"],
                      command=lambda: self.btn_click('9'), **cal_btn_style)
        btn_9.grid(row=0, column=2, padx=4, pady=4)

        btn_add = Button(btn_frame, text='+', bg=THEME["calculator"]["op_btn"], fg="white",
                        command=lambda: self.btn_click('+'), **cal_btn_style)
        btn_add.grid(row=0, column=3, padx=4, pady=4)

        btn_4 = Button(btn_frame, text='4', bg=THEME["calculator"]["num_btn"], fg=THEME["text"],
                      command=lambda: self.btn_click('4'), **cal_btn_style)
        btn_4.grid(row=1, column=0, padx=4, pady=4)

        btn_5 = Button(btn_frame, text='5', bg=THEME["calculator"]["num_btn"], fg=THEME["text"],
                      command=lambda: self.btn_click('5'), **cal_btn_style)
        btn_5.grid(row=1, column=1, padx=4, pady=4)

        btn_6 = Button(btn_frame, text='6', bg=THEME["calculator"]["num_btn"], fg=THEME["text"],
                      command=lambda: self.btn_click('6'), **cal_btn_style)
        btn_6.grid(row=1, column=2, padx=4, pady=4)

        btn_sub = Button(btn_frame, text='−', bg=THEME["calculator"]["op_btn"], fg="white",
                        command=lambda: self.btn_click('-'), **cal_btn_style)
        btn_sub.grid(row=1, column=3, padx=4, pady=4)

        btn_1 = Button(btn_frame, text='1', bg=THEME["calculator"]["num_btn"], fg=THEME["text"],
                      command=lambda: self.btn_click('1'), **cal_btn_style)
        btn_1.grid(row=2, column=0, padx=4, pady=4)

        btn_2 = Button(btn_frame, text='2', bg=THEME["calculator"]["num_btn"], fg=THEME["text"],
                      command=lambda: self.btn_click('2'), **cal_btn_style)
        btn_2.grid(row=2, column=1, padx=4, pady=4)

        btn_3 = Button(btn_frame, text='3', bg=THEME["calculator"]["num_btn"], fg=THEME["text"],
                      command=lambda: self.btn_click('3'), **cal_btn_style)
        btn_3.grid(row=2, column=2, padx=4, pady=4)

        btn_mul = Button(btn_frame, text='×', bg=THEME["calculator"]["op_btn"], fg="white",
                        command=lambda: self.btn_click('*'), **cal_btn_style)
        btn_mul.grid(row=2, column=3, padx=4, pady=4)

        btn_0 = Button(btn_frame, text='0', bg=THEME["calculator"]["num_btn"], fg=THEME["text"],
                      command=lambda: self.btn_click('0'), **cal_btn_style)
        btn_0.grid(row=3, column=0, padx=4, pady=4)

        btn_clear = Button(btn_frame, text='C', bg=THEME["calculator"]["clear_btn"], fg="white",
                         command=self.btn_clear, **cal_btn_style)
        btn_clear.grid(row=3, column=1, padx=4, pady=4)

        btn_equal = Button(btn_frame, text='=', bg=THEME["calculator"]["equal_btn"], fg="white",
                         command=self.btn_equal, **cal_btn_style)
        btn_equal.grid(row=3, column=2, padx=4, pady=4)

        btn_div = Button(btn_frame, text='÷', bg=THEME["calculator"]["op_btn"], fg="white",
                        command=lambda: self.btn_click('/'), **cal_btn_style)
        btn_div.grid(row=3, column=3, padx=4, pady=4)

        # Right side - Cart Frame - Moved up 5px
        cart_Frame = Frame(
            Cal_Cart_Frame,
            bg=THEME["surface"],
            relief="flat"
        )
        cart_Frame.place(x=282, y=0, width=318, height=450)

        # Cart Title - Improved visibility
        self.cartTitle = Label(
            cart_Frame,
            text="🛒 Cart \t Total Products: [0]",
            bg=THEME["primary"],
            font=("Segoe UI", 14, "bold"),
            fg="white",
            pady=8  # Added padding
        )
        self.cartTitle.pack(side=TOP, fill=X)

        # Cart Table Frame - Adjusted dimensions
        cart_table_frame = Frame(cart_Frame, bg=THEME["surface"])
        cart_table_frame.place(x=5, y=45, width=310, height=400)

        # Cart Table Scrollbars
        scrolly = Scrollbar(cart_table_frame, orient=VERTICAL)
        scrollx = Scrollbar(cart_table_frame, orient=HORIZONTAL)
        
        # Cart Table
        self.CartTable = ttk.Treeview(
            cart_table_frame,
            columns=("pid", "name", "price", "qty"),  # Added total column
            yscrollcommand=scrolly.set,
            xscrollcommand=scrollx.set,
            style="Custom.Treeview",
            height=15,
            selectmode='browse'  # Added selection mode
        )

        scrollx.pack(side=BOTTOM, fill=X)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.config(command=self.CartTable.xview)
        scrolly.config(command=self.CartTable.yview)
        self.CartTable.pack(fill=BOTH, expand=1)

        # Configure cart table columns
        self.CartTable.heading("pid", text="PID")
        self.CartTable.heading("name", text="Name")
        self.CartTable.heading("price", text="Price")
        self.CartTable.heading("qty", text="QTY")
        # self.CartTable.heading("total", text="Total")  # Added total heading
        
        # Show cart table headings
        self.CartTable["show"] = "headings"
        
        self.CartTable.column("pid", width=40, anchor=CENTER)
        self.CartTable.column("name", width=120, anchor=W)
        self.CartTable.column("price", width=70, anchor=CENTER)
        self.CartTable.column("qty", width=40, anchor=CENTER)
        # self.CartTable.column("total", width=70, anchor=CENTER)  # Added total column

        # Bind selection event
        self.CartTable.bind("<ButtonRelease-1>", self.user_get_data_cart)

        # Add to Cart Frame - Adjusted position and spacing
        Add_CartWidgetsFrame = Frame(
            self.root,
            bg=THEME["surface"],
            relief="flat",bd=1  # Removed border
        )
        Add_CartWidgetsFrame.place(x=501, y=660, width=600, height=125)  # Adjust y-coordinate


        lbl_p_name = Label(
            Add_CartWidgetsFrame,
            text="Product Name",
            font=("Segoe UI", 12, "bold"),
            bg=THEME["surface"]
        )
        lbl_p_name.place(x=5, y=5)

        # Product Name Entry
        pname_frame = create_modern_entry(
            Add_CartWidgetsFrame,
            textvariable=self.var_name,
            width=190,
            height=22,
            readonly=True
        )
        pname_frame.place(x=5, y=35)

        lbl_p_price = Label(
            Add_CartWidgetsFrame,
            text="Price Per Qty",
            font=("Segoe UI", 12, "bold"),
            bg=THEME["surface"]
        )
        lbl_p_price.place(x=230, y=5)

        # Price Entry
        price_frame = create_modern_entry(
            Add_CartWidgetsFrame,
            textvariable=self.var_price,
            width=150,
            height=22,
            readonly=True
        )
        price_frame.place(x=230, y=35)

        lbl_p_qty = Label(
            Add_CartWidgetsFrame,
            text="Quantity",
            font=("Segoe UI", 12, "bold"),
            bg=THEME["surface"]
        )
        lbl_p_qty.place(x=420, y=5)

        # Quantity Entry
        qty_frame = create_modern_entry(
            Add_CartWidgetsFrame,
            textvariable=self.var_qty,
            width=160,
            height=22
        )
        qty_frame.place(x=420, y=35)

        self.lbl_inStock = Label(
            Add_CartWidgetsFrame,
            text="In Stock",
            font=("Segoe UI", 12, "bold"),
            bg=THEME["surface"]
        )
        self.lbl_inStock.place(x=5, y=70)

        btn_clear_cart = Button(
            Add_CartWidgetsFrame,
            text="Clear",
            command=self.clear_cart_selection,
            font=("Segoe UI", 12, "bold"),
            bg=THEME["accent"],
            fg="white",
            cursor="hand2",
            relief="flat"
        )
        btn_clear_cart.place(x=180, y=70, width=150, height=35)

        btn_add_cart = Button(
            Add_CartWidgetsFrame,
            text="Add | Update Cart",
            command=self.user_add_update_cart,
            font=("Segoe UI", 12, "bold"),
            bg=THEME["success"],
            fg="white",
            cursor="hand2",
            relief="flat"
        )
        btn_add_cart.place(x=340, y=70, width=240, height=35)

        # Bill Area - Removed border
        BillFrame = Frame(
            self.root,
            bg=THEME["surface"],
            relief="flat"  # Removed border
        )
        BillFrame.place(x=1105, y=115, width=425, height=535)

        BTitle = Label(
            BillFrame,
            text="📝 Customer Bill",
            bg=THEME["primary"],
            font=("Segoe UI", 14, "bold"),
            fg="white",
            pady=5
        )
        BTitle.pack(side=TOP, fill=X)

        scrolly = Scrollbar(BillFrame, orient=VERTICAL)
        scrolly.pack(side=RIGHT, fill=Y)
        
        self.txt_bill_area = Text(
            BillFrame,
            yscrollcommand=scrolly.set,
            font=("Segoe UI", 12),
            bg=THEME["surface"]
        )
        self.txt_bill_area.pack(fill=BOTH, expand=1)
        scrolly.config(command=self.txt_bill_area.yview)
        self.txt_bill_area.config(state='disabled')

        # Bill Menu - Removed border
        BillMenuFrame = Frame(
            self.root,
            bg=THEME["surface"],
            relief="flat"  # Removed border
        )
        BillMenuFrame.place(x=1105, y=655, width=425, height=130)

        self.lbl_amnt = Label(
            BillMenuFrame,
            text="Bill Amount\n[0]",
            font=("Segoe UI", 12, "bold"),
            bg=THEME["info"],
            fg="white"
        )
        self.lbl_amnt.place(x=2, y=3, width=120, height=70)

        self.lbl_discount = Label(
            BillMenuFrame,
            text="Discount\n[5%]",
            font=("Segoe UI", 12, "bold"),
            bg=THEME["success"],
            fg="white"
        )
        self.lbl_discount.place(x=132, y=3, width=120, height=70)

        self.lbl_net_pay = Label(
            BillMenuFrame,
            text="Net Pay\n[0]",
            font=("Segoe UI", 12, "bold"),
            bg=THEME["primary"],
            fg="white"
        )
        self.lbl_net_pay.place(x=260, y=3, width=160, height=70)

        btn_print = Button(
            BillMenuFrame,
            text="🖨️ Print",
            command=self.print_bill,
            font=("Segoe UI", 12, "bold"),
            bg=THEME["success"],
            fg="white",
            cursor="hand2",
            relief="flat"
        )
        btn_print.place(x=2, y=78, width=120, height=50)

        btn_clear_all = Button(
            BillMenuFrame,
            text="🗑️ Clear All",
            command=self.clear_all,
            font=("Segoe UI", 12, "bold"),
            bg=THEME["accent"],
            fg="white",
            cursor="hand2",
            relief="flat"
        )
        btn_clear_all.place(x=132, y=78, width=120, height=50)

        btn_generate = Button(
            BillMenuFrame,
            text="📄 Generate Bill",
            command=self.generate_bill,
            font=("Segoe UI", 12, "bold"),
            bg=THEME["info"],
            fg="white",
            cursor="hand2",
            relief="flat"
        )
        btn_generate.place(x=260, y=78, width=160, height=50)

    def update_product_quantity(self):
        """Update product quantities in Firestore after bill generation"""
        try:
            # Get current products from Firestore
            products_ref = self.db.collection("All-Products").document("Products-List")
            doc = products_ref.get()
            products = doc.to_dict().get("Products", [])
            
            # Update quantities for products in cart
            for cart_item in self.cart_list:
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

    def clear_customer_fields(self):
        """Clear customer details fields"""
        self.var_cname.set("")
        self.var_contact.set("")

    def clear_all(self):
        """Clear all information including cart, bill area, and customer details"""
        # Clear customer details
        self.var_cname.set("")
        self.var_contact.set("")
        
        # Clear product selection
        self.var_pid.set("")
        self.var_name.set("")
        self.var_price.set("")
        self.var_qty.set("")
        self.lbl_inStock.config(text="In Stock")
        
        # Clear cart
        self.cart_list = []
        self.user_show_cart()
        
        # Reset billing amounts
        self.bill_amnt = 0
        self.net_pay = 0
        self.discount = 0
        self.user_bill_updates()
        
        # Clear bill area
        self.txt_bill_area.config(state='normal')
        self.txt_bill_area.delete('1.0', END)
        self.txt_bill_area.config(state='disabled')
        
        # Update cart title
        self.cartTitle.config(text=f"🛒 Cart \t Total Products: [0]")

    def generate_bill_number(self):
        """Generate a unique bill number using customer contact and timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        contact = self.var_contact.get().strip()[-4:]  # Last 4 digits of contact
        return f"BILL{contact}{timestamp}"


    def save_to_csv(self, bill_data):
        """Save bill details to CSV file"""
        try:
            # Get directory paths
            dirs = initialize_directories()
            if not dirs:
                raise Exception("Failed to initialize directories")
                
            # Create CSV file path
            csv_file = dirs['csv_files'] / "bills.csv"
            
            # Ensure directory exists
            csv_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists
            file_exists = csv_file.exists()
            
            # Prepare data for CSV
            csv_data = {
                'bill_number': self.bill_number,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'customer_name': self.var_cname.get(),
                'customer_contact': self.var_contact.get(),
                'total_amount': self.bill_amnt,
                'discount': self.discount,
                'net_amount': self.net_pay
            }
            
            # Write to CSV
            with open(csv_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=csv_data.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(csv_data)
            
            logging.info(f"Bill saved to CSV: {csv_file}")
            return True
                
        except Exception as e:
            logging.error(f"Failed to save bill to CSV: {str(e)}")
            messagebox.showerror("Error", f"Failed to save bill to CSV: {str(e)}")
            return False

    def save_bill_to_firestore(self, bill_data):
        """Save bill to Firestore"""
        try:
            # Convert cart items to proper format for Firestore
            cart_items = []
            for item in self.cart_list:
                cart_item = {
                    "pid": item[0],
                    "name": item[1],
                    "price": float(item[2]),
                    "quantity": int(item[3]),
                    "total": float(item[4])}
                
                cart_items.append(cart_item)
            
            # Update bill data with formatted cart items
            bill_data["items"] = cart_items
            
            # Save to Firestore
            self.db.collection("Bills").document(bill_data["bill_number"]).set(bill_data)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save bill to Firestore: {str(e)}")
            return False

    def search_bill(self, contact_number=None, bill_number=None):
        """Search for bills by contact number or bill number"""
        try:
            if not contact_number and not bill_number:
                messagebox.showerror("Error", "Please provide either contact number or bill number")
                return None
            
            csv_file = "bills/csv/bills.csv"
            if not os.path.exists(csv_file):
                messagebox.showerror("Error", "No bills found")
                return None
            
            df = pd.read_csv(csv_file)
            
            if contact_number:
                result = df[df['customer_contact'] == contact_number]
            else:
                result = df[df['bill_number'] == bill_number]
            
            if result.empty:
                messagebox.showinfo("Info", "No bills found")
                return None
            
            return result
        except Exception as e:
            messagebox.showerror("Error", f"Error searching bills: {str(e)}")
            return None

    def clear_cart_selection(self):
        """Clear customer details and product selection fields"""
        # Clear customer details
        self.var_cname.set("")
        self.var_contact.set("")
        
        # Clear product selection fields
        self.var_pid.set("")
        self.var_name.set("")
        self.var_price.set("")
        self.var_qty.set("")
        self.lbl_inStock.config(text="In Stock")

    def print_bill(self, bill_data=None):
        """Save the bill to file and CSV, and update stock quantities"""
        try:
            # Check if bill area is empty
            if not self.txt_bill_area.get('1.0', END).strip():
                self.log_action("Error", "Empty bill")
                messagebox.showerror("Error", "Please generate a bill first")
                return
                
            # Get bill text and generate bill number
            bill_text = self.txt_bill_area.get('1.0', END)
            
            # Use provided bill number or generate new one
            if bill_data and 'bill_number' in bill_data:
                bill_no = bill_data['bill_number']
            else:
                bill_no = f"BILL{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Get directory paths
            dirs = initialize_directories()
            if not dirs:
                raise Exception("Failed to initialize directories")
            
            # Create bill path using the bills directory
            bill_path = dirs['bills'] / f"{bill_no}.txt"
            
            # Ensure directory exists
            bill_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write bill to file
            with open(bill_path, 'w') as f:
                f.write(bill_text)
            
            # Prepare data for CSV with improved formatting
            csv_data = {
                'Bill Number': bill_no,
                'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Customer Name': self.var_cname.get(),
                'Customer Contact': self.var_contact.get(),
                'Total Amount': f"Rs. {self.bill_amnt:,.2f}",  # Format as currency
                'Discount': f"Rs. {self.discount:,.2f}",        # Format as currency
                'Net Pay': f"Rs. {self.net_pay:,.2f}"           # Format as currency
            }
            
            # Save to CSV
            self.save_to_csv(csv_data)
            
            # Update product quantities in Firestore
            if self.update_product_quantity():
                messagebox.showinfo("Success", "Bill has been saved and stock updated successfully!")
            else:
                messagebox.showwarning("Warning", "Bill saved, but stock update failed.")
            
            self.log_action("Print Bill", f"Bill saved: {bill_no}")
            
        except Exception as e:
            self.log_action("Error", f"Bill printing failed: {str(e)}")
            logging.error(traceback.format_exc())
            messagebox.showerror("Error", f"Error in saving bill: {str(e)}")

    def save_to_csv(self, bill_data):
        """Save bill details to CSV file"""
        try:
            # Get directory paths
            dirs = initialize_directories()
            if not dirs:
                raise Exception("Failed to initialize directories")
                
            # Create CSV file path
            csv_file = dirs['csv'] / "bills.csv"
            
            # Ensure directory exists
            csv_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists
            file_exists = csv_file.exists()
            
            # Write to CSV
            with open(csv_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=bill_data.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(bill_data)
            
            logging.info(f"Bill saved to CSV: {csv_file}")
            return True
                
        except Exception as e:
            logging.error(f"Failed to save bill to CSV: {str(e)}")
            messagebox.showerror("Error", f"Failed to save bill to CSV: {str(e)}")
            return False

    def save_to_csv(self, bill_data):
        """Save bill details to CSV file"""
        try:
            # Get directory paths
            dirs = initialize_directories()
            if not dirs:
                raise Exception("Failed to initialize directories")
                
            # Create CSV file path
            csv_file = dirs['csv'] / "bills.csv"
            
            # Ensure directory exists
            csv_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists
            file_exists = csv_file.exists()
            
            # Write to CSV
            with open(csv_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=bill_data.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(bill_data)
            
            logging.info(f"Bill saved to CSV: {csv_file}")
            return True
                
        except Exception as e:
            logging.error(f"Failed to save bill to CSV: {str(e)}")
            messagebox.showerror("Error", f"Failed to save bill to CSV: {str(e)}")
            return False

    def validate_contact(self, contact):
        """Validate customer contact number"""
        # Remove any spaces or special characters
        contact = ''.join(filter(str.isdigit, contact))
        
        # Check if it's a 10-digit number
        if len(contact) != 10:
            return False, "Contact number must be 10 digits"
            
        return True, contact

    def validate_customer_details(self):
        """Validate customer details before bill generation"""
        # Validate customer name
        name = self.var_cname.get().strip()
        if not name:
            return False, "Customer name is required"
        
        # Validate contact number
        contact = self.var_contact.get().strip()
        is_valid, result = self.validate_contact(contact)
        if not is_valid:
            return False, result
            
        # Update contact field with formatted number
        self.var_contact.set(result)
        return True, "Valid"

    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

    def __del__(self):
        """Cleanup when the window is closed"""
        try:
            # Clear cache
            self.clear_cache()
            
            # Close logging handlers
            if hasattr(self, 'logger') and self.logger:
                handlers = self.logger.handlers[:]
                for handler in handlers:
                    handler.close()
                    self.logger.removeHandler(handler)
                logging.info("Application terminated")
            
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
    def btn_click(self, num):
        """Handle calculator button clicks"""
        try:
            current = self.var_cal_input.get()
            self.var_cal_input.set(current + str(num))
        except Exception as e:
            messagebox.showerror("Error", f"Calculator input error: {str(e)}")

    def btn_clear(self):
        """Clear calculator input"""
        try:
            self.var_cal_input.set('')
        except Exception as e:
            messagebox.showerror("Error", f"Calculator clear error: {str(e)}")

    def btn_equal(self):
        """Calculate result"""
        try:
            result = eval(self.var_cal_input.get())
            self.var_cal_input.set(result)
        except Exception as e:
            messagebox.showerror("Error", "Invalid calculation")
            self.var_cal_input.set('')


    def system_logout(self):
        """Handle system logout"""
        try:
            if messagebox.askyesno("Confirm", "Do you want to logout?"):
                logging.info("User logged out successfully")  # Using logging directly
                self.running = False  # Stop any running processes
                if hasattr(self, 'clock_update_id'):
                    self.root.after_cancel(self.clock_update_id)  # Cancel the clock update
                self.root.destroy()  # Close the current window
                
                # Lazy import of LoginWindow
                from src.gui.login_window import LoginWindow  # Import here to avoid circular import
                login_window = LoginWindow()  # Create an instance of LoginWindow
                login_window.window.mainloop()
                
        except Exception as e:
            self.log_action("Error", f"Logout failed: {str(e)}")
            messagebox.showerror("Error", f"Error during logout: {str(e)}")

    def clear_cache(self):
        """Clear temporary files and QR codes"""
        try:
            # Clear QR codes
            qr_dir = "bills/qr_codes"
            if os.path.exists(qr_dir):
                shutil.rmtree(qr_dir)
                os.makedirs(qr_dir)
                
            # Clear temporary files
            temp_dir = tempfile.gettempdir()
            pattern = "bill_*.txt"
            for file in glob.glob(os.path.join(temp_dir, pattern)):
                try:
                    os.remove(file)
                except Exception as e:
                    logging.error(f"Failed to remove temp file {file}: {str(e)}")
                    
            # Force garbage collection
            gc.collect()
            
            logging.info("Cache cleared successfully")
            
        except Exception as e:
            logging.error(f"Error clearing cache: {str(e)}")
            traceback.print_exc()

    def log_action(self, action_type, message):
        """Log system actions with timestamp"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logging.info(f"{timestamp} - {action_type}: {message}")
        except Exception as e:
            print(f"Logging failed: {str(e)}")
