"""
Admin window GUI module.
"""
# Standard library imports
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Tkinter imports
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

# Logging imports
import logging
import logging.handlers
import gc
  
from src.core.product_functions import fetch_products, create_product,modify_product
from src.core.setup import initialize_directories

# Load environment variables from .env file
load_dotenv()

# Create a credentials object from environment variables
cred = credentials.Certificate({
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCycdi7+61ZYtsZ\ntRkR8n/OJouaL8l/fwLHXmYpwaSaot5EqdSfMeAvavE+9KlmXVksE/eNDkQMOYrB\nLnfTjnu9R7GvN1CzbeVn3kn66FFZLSfUlkSFDXLrfrv4R/ug7q+ir0+/rAbnpYJ/\nf06TuTL9uy4PNYD5BIsvQHALbxkIoin4NBC7TKn0zVBqVroWi8G+uTK99k3aRwCs\n3zLi6JYSS84pFJPbl62mLYq52TrCNPGjhVtArnOLH+s1t5KuQDkT4ubpILFb7xbm\nGf/Z+z4NJPiUM3f+XvL/mzNkCUtScwr2oJW2n35Z2b73wjCtx29H0onntOtarPcm\nBdwlARNZAgMBAAECggEAIHYZaUkFZedX2DtbjipBGa1lY+0hiLIAPWhsyVfSq9bI\n/FCwvy0BjV60+DDlyBtfJ2eSdvSLaHXnSfE8Fx4qYGp0Zl13rsxlGRoU9zHf6osO\nXdvgJxwlNbXeV/IwUjxZcwzVQxb2QpmXPb5Y+wKLxiCQ5m9jQOmUsEnWmB3jvfAD\nlAPCtUfcg7TQHsgtiNNQrXOdPu/xHJEGr7jC13BDBNNwO8oQNc8dgKtfhfUOhLNF\nd9a165SB2u7Cyz6YFYTwVHCQhz6KDG/dRD0+NU7Hn/gUe95c/JBUDiEn9cS9k2nt\nY50Rr8cGyRzfjCbQ0m1ONvVr3uaLeiiGjLWjfKJWCQKBgQD1fGRkhykKp8sxXPOi\nKQs5pRMC9Iho7iV4K4d/FgYh/0eELW9isjrZc2ilc8JV1E8zi7xpMl6xENPgIFnI\nl0Ylixa/I2MLg1uDj45YT9pR33JDxXQkd/r+gbZ+LutOi8piJa01glZ04+eEZbC+\ngXq4KYhk/ONh1Uj7fuhWyaINEwKBgQC6FmMtD8t1exqEq7jOeAbrddj6Ab+peXZ0\nAQhIj3LI03J3F7m4W5SsWWbMFDeF2juWbhopRymiy7WGKoJDy7a9kff7dNnV4aPQ\nv5R93svpq+wSeTlcIx1Lv3IVYuHgmamLR4OlVC3BGBLwd5ASgYtcBkptUSZC3C8Z\n/Sy4MuuHYwKBgEAGupRxoCW0T83HJZAkzlWxlTzPFIjxm/o0uDlQQDc7wqZZx1Rh\nkfHHJQMKJySFpEaYaoKxbXsXHXu2VFR6CASgu0UM8Lc/Am5U0dZ8tT9nXQEKDdm5\nJVCd+j/88shgs19X3k43eV8xVd/1OdzmHmDMDFPylUed/lQB7I0+N7LbAoGAcsFh\nkaVe4+jxloVLZ1APfF7lWm9/oWR9DtagJBcKQxxaR2UDK9SWH57WTN3ey5WkD4WA\nbpoq6/DR1ZYbVPGolMkScyhBOat3WUD7so+VkllqMI4/ODmTVGYQVW3wO5CnRHPq\nlCcQPDa7Xz1sRG1M4ogil71mae7cwRsm28TTCF8CgYEAo9JXa6dxWWJ6cTzLYvyV\nOIFMZPY6G8kT1w17FjeY1ddvzmgAOZI0Omytm6GhwHh4OgUt4E88v/DgtKQCh2mQ\n6fLPZKc1//jOFp56uQ7IXEG1LUXJYcikLrwBUXMbfIfPSw7D/VxgWL+Fhh5/Go5M\nBCLhpvsZOIE/n/nwkwVOK9Q=\n-----END PRIVATE KEY-----\n",  # Ensure newlines are handled
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
})

class ThemeManager:
    # Theme definitions
    THEMES = {
        "dark": {
            "primary": "#1a237e",      # Dark blue
            "secondary": "#2ecc71",     # Green
            "background": "#2c3e50",    # Dark slate
            "surface": "#34495e",       # Lighter slate
            "text": "#ecf0f1",         # Almost white
            "accent": "#e74c3c",       # Red
            "input_bg": "#445565",     # Slate blue
            "header_bg": "#1a237e",    # Dark blue
            "subheader_bg": "#5b6c72", # Gray blue
            "button_hover": "#27ae60", # Darker green
            "error": "#c0392b",        # Dark red
        },
        "light": {
            "primary": "#3498db",      # Blue
            "secondary": "#2ecc71",     # Green
            "background": "#f0f2f5",    # Light gray
            "surface": "#ffffff",       # White
            "text": "#2c3e50",         # Dark slate
            "accent": "#e74c3c",       # Red
            "input_bg": "#f8f9fa",     # Very light gray
            "header_bg": "#3498db",    # Blue
            "subheader_bg": "#bdc3c7", # Light gray
            "button_hover": "#27ae60", # Darker green
            "error": "#c0392b",        # Dark red
        },
        "blue": {
            "primary": "#1976D2",      # Blue
            "secondary": "#64B5F6",     # Light blue
            "background": "#E3F2FD",    # Very light blue
            "surface": "#BBDEFB",       # Lighter blue
            "text": "#1565C0",         # Dark blue
            "accent": "#2196F3",       # Blue
            "input_bg": "#FFFFFF",     # White
            "header_bg": "#1976D2",    # Blue
            "subheader_bg": "#90CAF9", # Light blue
            "button_hover": "#1565C0", # Darker blue
            "error": "#F44336",        # Red
        }
    }
    @classmethod
    def get_theme(cls, theme_name="dark"):
        return cls.THEMES.get(theme_name, cls.THEMES["dark"])

class AdminIMS:
    def __init__(self, root):
        # Initialize Firebase if not already initialized
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(cred)
            

        self.root = root
        self.root.attributes('-fullscreen', True)  # Enable full screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.configure(bg="#f0f2f5")
        self.root.state('zoomed')
        
        # Initialize all StringVar variables
        self.var_search = tk.StringVar()  # Add this line
        self.var_searchtype = tk.StringVar()
        self.var_searchtxt = tk.StringVar()
        self.var_searchby = tk.StringVar()
        self.var_pid = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_price = tk.StringVar()
        self.var_qty = tk.StringVar()
        
        # User management variables
        self.var_user_id = tk.StringVar()
        self.var_username = tk.StringVar()
        self.var_password = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_user_role = tk.StringVar()
        self.var_user_search = tk.StringVar()
        self.var_user_searchtype = tk.StringVar()

        self.var_pid = StringVar()
        self.var_product_name = StringVar()
        self.var_product_price = StringVar()
        self.var_product_qty = StringVar()
        self.var_searchtype = StringVar()
        self.var_search = StringVar()
        
        # Initialize database connection
        self.db = firestore.client()
        
        # Initialize theme and bills directory
        self.theme = ThemeManager.get_theme()
        self.bills_dir = "bills/"
        
        self.running = True
        
        # Create UI
        self.create_system_header()
        self.create_system_content()

    def create_system_header(self):
        # Main Header Frame with gradient effect
        self.header_frame = Frame(self.root, height=80, bg="#1a237e")
        self.header_frame.pack(side=TOP, fill=X)

        # Company Logo/Name
        self.logo_frame = Frame(self.header_frame, bg="#1a237e")
        self.logo_frame.pack(side=LEFT, padx=20)

        self.title_label = Label(
            self.logo_frame,
            text="🏪 Modern Inventory",
            font=("Helvetica", 24, "bold"),
            bg="#1a237e",
            fg="white"
        )
        self.title_label.pack(side=LEFT, pady=15)

        # Right side controls
        self.controls_frame = Frame(self.header_frame, bg="#1a237e")
        self.controls_frame.pack(side=RIGHT, padx=20)

        # Clock and Date
        self.datetime_frame = Frame(self.controls_frame, bg="#1a237e")
        self.datetime_frame.pack(side=LEFT, padx=20)

        self.clock_label = Label(
            self.datetime_frame,
            text="",
            font=("Helvetica", 12),
            bg="#1a237e",
            fg="#90caf9"
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
            command=self.system_logout,
            padx=20,
            pady=5
        )
        self.logout_button.pack(side=LEFT, pady=15)
        
        # Bind hover effects
        self.logout_button.bind("<Enter>", lambda e: self.logout_button.config(
            bg="#ff1744"))
        self.logout_button.bind("<Leave>", lambda e: self.logout_button.config(
            bg="#ff5252"))

        # Sub Header with navigation info
        self.sub_header = Frame(self.root, bg="#283593", height=40)
        self.sub_header.pack(side=TOP, fill=X)

        self.nav_label = Label(
            self.sub_header,
            text="📍 Dashboard",
            font=("Helvetica", 12),
            bg="#283593",
            fg="#e8eaf6"
        )
        self.nav_label.pack(side=LEFT, padx=20, pady=8)

        # Start clock update
        self.update_system_clock()

    def update_system_clock(self):
        if not self.running:
            return
            
        current_time = time.strftime("%I:%M:%S %p")
        current_date = time.strftime("%d %B, %Y")
        self.clock_label.config(
                text=f"🗓️ {current_date}\n⏰ {current_time}")
        
        if self.running:
            self.clock_update_id = self.root.after(1000, self.update_system_clock)


    def system_logout(self):
        """Handle system logout"""
        try:
            if messagebox.askyesno("Confirm", "Do you want to logout?"):
                logging.info("Admin logged out successfully")  # Using logging directly
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

    def log_action(self, action_type, message):
        """Log system actions with timestamp"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logging.info(f"{timestamp} - {action_type}: {message}")
        except Exception as e:
            print(f"Logging failed: {str(e)}")

            
    def create_system_content(self):
        # Style the notebook
        style = ttk.Style()
        style.configure("Custom.TNotebook", background="#f0f2f5")
        style.configure("Custom.TNotebook.Tab", 
                       padding=[12, 8],
                       font=('Helvetica', 10, 'bold'))
        
        self.notebook = ttk.Notebook(self.root, style="Custom.TNotebook")
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Create frames for each tab
        self.products_frame = Frame(self.notebook, bg="#f0f2f5")
        self.bills_frame = Frame(self.notebook, bg=self.theme["background"])
        self.user_frame = Frame(self.notebook, bg="#f0f2f5")  # Add this line

        # Add tabs to notebook
        self.notebook.add(self.products_frame, text=" 📦 Products ")
        self.notebook.add(self.bills_frame, text=" 💰 Sales ")
        self.notebook.add(self.user_frame, text=" 👥 Users ")  # Add this line

        # Setup interfaces
        self.setup_product_interface()
        self.setup_bills_interface()
        self.setup_users_interface()  # Add this line

    def setup_bills_interface(self):
        # Title Frame
        title_frame = Frame(self.bills_frame, bg=self.theme["primary"])
        title_frame.pack(fill=X, pady=10)
        
        title = Label(
            title_frame,
            text="Bills History",
            font=("Helvetica", 18, "bold"),
            bg=self.theme["primary"],
            fg=self.theme["text"],
            pady=15
        )
        title.pack()

        # Main Content Area - Split into two panels
        content_frame = Frame(self.bills_frame, bg=self.theme["background"])
        content_frame.pack(fill=BOTH, expand=True, padx=30, pady=10)
        
        # Left Panel - Bills List
        left_frame = LabelFrame(
            content_frame,
            text=" Bills ",
            font=("Segoe UI", 12, "bold"),
            bg=self.theme["surface"],
            fg=self.theme["text"],
            relief=FLAT,
            bd=0
        )
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=5)

        # Bills Listbox with Scrollbar
        self.bills_listbox = Listbox(
            left_frame,
            font=("Segoe UI", 11),
            bg=self.theme["input_bg"],
            fg=self.theme["text"],
            selectmode=SINGLE,
            relief=FLAT,
            selectbackground=self.theme["primary"],
            bd=0
        )
        self.bills_listbox.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
        
        scrollbar_left = Scrollbar(left_frame, orient="vertical", command=self.bills_listbox.yview)
        scrollbar_left.pack(side=RIGHT, fill="y", pady=10)
        self.bills_listbox.config(yscrollcommand=scrollbar_left.set)

        # Right Panel - Bill Content
        right_frame = LabelFrame(
            content_frame,
            text=" Bill Details ",
            font=("Segoe UI", 12, "bold"),
            bg=self.theme["surface"],
            fg=self.theme["text"],
            relief=FLAT,
            bd=0
        )
        right_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=5)

        # Bill Content Text Widget with Scrollbar
        self.bill_content = Text(
            right_frame,
            font=("Consolas", 11),
            bg=self.theme["input_bg"],
            fg=self.theme["text"],
            relief=FLAT,
            wrap=WORD,
            padx=10,
            pady=10
        )
        self.bill_content.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
        
        scrollbar_right = Scrollbar(right_frame, orient="vertical", command=self.bill_content.yview)
        scrollbar_right.pack(side=RIGHT, fill="y", pady=10)
        self.bill_content.config(yscrollcommand=scrollbar_right.set)

        # Bind selection event
        self.bills_listbox.bind('<<ListboxSelect>>', self.show_bill_content)
        
        # Add this line at the end of setup_bills_interface
        self.load_bills()  # Load bills when interface is set up

    def load_bills(self):
        """Load all bill files from the bills directory"""
        try:
            # Clear existing items
            self.bills_listbox.delete(0, END)
            
            # Get directories from initialize_directories
            dirs = initialize_directories()
            if not dirs:
                raise Exception("Failed to initialize directories")
            
            # Get bills directory path
            bills_dir = dirs['bills']
            
            # Get all .txt files from bills directory
            bills = [f for f in os.listdir(bills_dir) if f.endswith('.txt')]
            
            # Sort bills by modification time (newest first)
            bills.sort(key=lambda x: os.path.getmtime(bills_dir / x), reverse=True)
            
            # Add bills to listbox with icons and formatting
            for bill in bills:
                # Format the display name (remove .txt and add icon)
                display_name = f" 📄 {bill.replace('.txt', '')}"
                self.bills_listbox.insert(END, display_name)
                
            # Store bills_dir for use in show_bill_content
            self.bills_dir = bills_dir
                
        except Exception as e:
            logging.error(f"Error loading bills: {str(e)}")
            messagebox.showerror("Error", f"Error loading bills: {str(e)}")

    def show_bill_content(self, event):
        """Display the content of the selected bill"""
        try:
            # Clear current content
            self.bill_content.delete(1.0, END)
            
            # Get selected bill
            selection = self.bills_listbox.curselection()
            if not selection:
                return
                
            # Get bill name (remove icon and add .txt back)
            bill_name = self.bills_listbox.get(selection[0]).strip(" 📄 ") + ".txt"
            bill_path = self.bills_dir / bill_name
            
            # Read and display bill content
            if bill_path.exists():
                with open(bill_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                # Enable text widget for writing
                self.bill_content.config(state='normal')
                
                # Add some formatting to the content
                self.bill_content.insert(END, "═" * 50 + "\n")
                self.bill_content.insert(END, f"   {bill_name}\n")
                self.bill_content.insert(END, "═" * 50 + "\n\n")
                self.bill_content.insert(END, content)
                
                # Make text widget read-only
                self.bill_content.config(state='disabled')
            else:
                self.bill_content.insert(END, "Bill file not found.")
                
        except Exception as e:
            logging.error(f"Error displaying bill: {str(e)}")
            messagebox.showerror("Error", f"Error displaying bill: {str(e)}")

    def _bind_hover_events(self, widget):
        original_color = widget.cget("background")
        darker_color = self._darken_color(original_color)
        
        widget.bind("<Enter>", lambda e: widget.config(bg=darker_color))
        widget.bind("<Leave>", lambda e: widget.config(bg=original_color))

    def _darken_color(self, color):
        # Convert hex to RGB, darken, and convert back to hex
        # This is a simplified version - you might want to add proper color manipulation
        return color  # For now, returning the same color

    def display_products(self):
        try:
            self.product_table.delete(*self.product_table.get_children())
            products = fetch_products()
            
            for product in products:
                self.product_table.insert('', 'end', values=(
                    product.get('PID', ''),
                    product.get('Name', ''),
                    product.get('Price', ''),
                    product.get('QTY', '')
                ))
        except Exception as ex:
            messagebox.showerror("Error", f"Error fetching products: {str(ex)}")

    def populate_fields(self, ev):
        try:
            selected_row = self.product_table.focus()
            contents = self.product_table.item(selected_row)
            row = contents['values']
            
            if row:
                self.var_product_name.set(row[1])
                self.var_product_price.set(row[2])
                self.var_product_qty.set(row[3])
        except Exception as ex:
            messagebox.showerror("Error", f"Error populating fields: {str(ex)}")

    def add_new_product(self):
        try:
            # Validate product name
            if self.var_product_name.get() == "":
                messagebox.showerror("Error", "Product name is required")
                return
            
            # Fetch existing products to determine the next PID
            products_ref = self.db.collection('All-Products').document('Products-List')
            doc = products_ref.get()
            
            if not doc.exists:
                current_products = []
            else:
                current_products = doc.to_dict().get('Products', [])
            
            # Generate new PID based on existing products
            if current_products:
                # Assuming PID is in the format "PID{number}"
                existing_pids = [int(product['PID'][3:]) for product in current_products if product['PID'].startswith("PID")]
                new_pid_number = max(existing_pids) + 1  # Increment the highest existing PID
            else:
                new_pid_number = 1  # Start from 1 if no products exist
            
            new_pid = f"PID{new_pid_number}"  # Create new PID
            
            # Create new product record
            create_product(
                name=self.var_product_name.get(),
                pid=new_pid,
                price=float(self.var_product_price.get()),
                qty=int(self.var_product_qty.get())
            )
            messagebox.showinfo("Success", "Product Added Successfully")
            self.display_products()
            self.clear_fields()
        except Exception as ex:
            messagebox.showerror("Error", f"Error adding product: {str(ex)}")

    
    
    def update_product(self):
        try:
            selected_item = self.product_table.selection()
            if not selected_item:
                messagebox.showerror("Error", "Please select a product to update")
                return

            values = self.product_table.item(selected_item)['values']
            if values:
                # Assuming values are in the order: PID, Name, Price, Quantity
                pid = values[0]  # Get the PID of the selected product
                name = self.var_product_name.get()  # Get updated name from the entry
                price = float(self.var_product_price.get())  # Get updated price from the entry
                qty = int(self.var_product_qty.get())  # Get updated quantity from the entry
                
                # Call modify_product with the necessary parameters
                modify_product(pid, name, price, qty)  # Ensure modify_product accepts these parameters
                
                messagebox.showinfo("Success", "Product updated successfully")
                self.display_products()
                self.clear_fields()
        except Exception as ex:
            messagebox.showerror("Error", f"Error updating product: {str(ex)}")

    def delete_product(self):
        try:
            # Get selected item from the table
            selected_item = self.product_table.selection()
            if not selected_item:
                messagebox.showerror("Error", "Please select a product to delete")
                return

            # Confirm deletion
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?")
            if confirm:
                # Retrieve selected product details
                values = self.product_table.item(selected_item)['values']
                if values:
                    product_pid = values[0]  # Assuming PID is in the first column
                    
                    # Fetch the Products-List document
                    products_ref = self.db.collection('All-Products').document('Products-List')
                    doc = products_ref.get()
                    
                    if doc.exists:
                        products = doc.to_dict().get('Products', [])
                        
                        # Filter out the product to delete
                        updated_products = [
                            product for product in products if product.get('PID') != product_pid
                        ]
                        
                        if len(updated_products) == len(products):
                            messagebox.showerror("Error", "Product not found in the database")
                            return

                        # Update Firestore with the new product list
                        products_ref.set({'Products': updated_products})
                        
                        # Notify user of success
                        messagebox.showinfo("Success", "Product deleted successfully")
                        
                        # Clear fields and refresh the product table
                        self.clear_fields()
                        self.display_products()
                    else:
                        messagebox.showerror("Error", "Products list does not exist in the database")
        except Exception as ex:
            logging.error(f"Error deleting product: {str(ex)}")
            messagebox.showerror("Error", f"Error deleting product: {str(ex)}")

    def clear_fields(self):
        """Clear all product fields and refresh table"""
        try:
            # Clear all input fields
            self.var_product_name.set("")
            self.var_product_price.set("")
            self.var_product_qty.set("")  # Reset to default
            self.var_search.set("")
            self.var_searchtype.set("Select")

            # Clear any table selection
            if hasattr(self, 'product_table'):
                self.product_table.selection_remove(*self.product_table.selection())

            # Refresh table to show all products
            self.display_products()

            logging.info("Product fields cleared and table refreshed")

        except Exception as e:
            logging.error(f"Error clearing product fields: {str(e)}")
            messagebox.showerror("Error", f"Error clearing fields: {str(e)}")

    def search_products(self):
            """Search products based on selected criteria"""
            try:
                if self.var_searchtype.get() == "Select":
                    messagebox.showerror("Error", "Please select search criteria")
                    return
                
                search_term = self.var_search.get()
                if not search_term:
                    messagebox.showerror("Error", "Please enter search term")
                    return

                # Clear current table
                self.product_table.delete(*self.product_table.get_children())
                
                # Get products document
                doc = self.db.collection('All-Products').document('Products-List').get()
                
                if not doc.exists:
                    messagebox.showinfo("Info", "No products found")
                    return
                    
                # Get products list
                products = doc.to_dict().get('Products', [])
                found = False
                
                # Map search type to product field
                field_map = {
                    "PID": "PID",
                    "Name": "Name"
                }
                
                search_field = field_map.get(self.var_searchtype.get())
                if not search_field:
                    messagebox.showerror("Error", "Invalid search type")
                    return
                    
                # Search through products
                for product in products:
                    if search_field in product:
                        field_value = str(product[search_field]).lower()
                        if field_value.startswith(search_term.lower()):
                            found = True
                            self.product_table.insert('', 'end', values=(
                                product.get('PID', ''),
                                product.get('Name', ''),
                                product.get('Price', ''),
                                product.get('QTY', ''),
                            ))
                
                if not found:
                    messagebox.showinfo("Info", "No matching products found")
                    self.display_products()  # Show all products if no matches
                    
            except Exception as e:
                logging.error(f"Error searching products: {str(e)}")
                messagebox.showerror("Error", f"Error searching products: {str(e)}")


    def setup_product_interface(self):
        # Title Frame
        title_frame = tk.Frame(self.products_frame, bg="#1a237e")
        title_frame.pack(fill=tk.X)
        
        title = tk.Label(
            title_frame,
            text="Product Management",
            font=("Helvetica", 20, "bold"),
            bg="#1a237e",
            fg="white",
            pady=10
        )
        title.pack()

        # Search Frame with better styling
        search_frame = tk.LabelFrame(
            self.products_frame,
            text="Search Products",
            font=("Helvetica", 12, "bold"),
            bg="white",
            pady=15,
            padx=15,
            relief="groove"
        )
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        # Search Type Label and Dropdown
        tk.Label(
            search_frame,
            text="Search By:",
            font=("Helvetica", 11, "bold"),
            bg="white",
            fg="#2C3E50"
        ).pack(side=tk.LEFT, padx=5)

        # Style for Combobox
        style = ttk.Style()
        style.configure(
            "Custom.TCombobox",
            background="#F7F9FC",
            fieldbackground="#F7F9FC",
            selectbackground="#3498DB",
            selectforeground="white"
        )

        search_combo = ttk.Combobox(
            search_frame,
            textvariable=self.var_searchtype,
            values=("Select", "Name", "PID"),
            state="readonly",
            width=15,
            style="Custom.TCombobox"
        )
        search_combo.pack(side=tk.LEFT, padx=5)
        search_combo.current(0)

        # Entry frame for border effect
        entry_frame = tk.Frame(
            search_frame,
            bg="#E0E7FF",  # Border color
            padx=1,
            pady=1
        )
        entry_frame.pack(side=tk.LEFT, padx=10)

        # Search Entry with styling
        search_entry = tk.Entry(
            entry_frame,
            textvariable=self.var_search,
            font=("Helvetica", 11),
            bg="#F7F9FC",
            fg="#2C3E50",
            relief="flat",
            width=25,
            highlightthickness=0,
            bd=0
        )
        search_entry.pack(ipady=5, padx=1)

        # Bind focus events for highlight effect
        search_entry.bind("<FocusIn>", lambda e: entry_frame.configure(bg="#3498DB"))
        search_entry.bind("<FocusOut>", lambda e: entry_frame.configure(bg="#E0E7FF"))

        # Button style
        button_style = {
            "font": ("Helvetica", 10, "bold"),
            "relief": "flat",
            "cursor": "hand2",
            "padx": 15,
            "pady": 5
        }

        # Search Button
        search_btn = tk.Button(
            search_frame,
            text="Search",
            bg="#3498DB",
            fg="white",
            activebackground="#2980B9",command=self.search_products,
            activeforeground="white",
            **button_style
        )
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear Button
        clear_btn = tk.Button(
            search_frame,
            text="Clear",
            bg="#95A5A6",
            fg="white",
            activebackground="#7F8C8D",command=self.clear_fields,
            activeforeground="white",
            **button_style
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        # Add hover effects for buttons
        for btn, colors in [(search_btn, ("#3498DB", "#2980B9")), 
                           (clear_btn, ("#95A5A6", "#7F8C8D"))]:
            btn.bind("<Enter>", lambda e, b=btn, c=colors[1]: b.configure(bg=c))
            btn.bind("<Leave>", lambda e, b=btn, c=colors[0]: b.configure(bg=c))

        # Product Details Frame
        details_frame = tk.LabelFrame(
            self.products_frame,
            text="Product Details",
            font=("Helvetica", 12, "bold"),
            bg="white",
            pady=15,
            padx=15,
            relief="groove"
        )
        details_frame.pack(fill=tk.X, padx=10, pady=10)

        # Left frame for product details
        left_frame = tk.Frame(details_frame, bg="white")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Custom style for entry boxes
        entry_style = {
            "font": ("Helvetica", 11),
            "bg": "#F7F9FC",  # Light blue-grey background
            "fg": "#2C3E50",  # Dark blue-grey text
            "relief": "flat",
            "bd": 0,
            "highlightthickness": 1,
            "highlightbackground": "#E0E7FF",  # Light border color
            "highlightcolor": "#3498DB",  # Blue highlight on focus
        }

        # Product Details Fields in one line
        labels = ["Product Name:", "Price:", "Quantity:"]
        variables = [self.var_product_name, self.var_product_price, self.var_product_qty]
        
        for i, (label, var) in enumerate(zip(labels, variables)):
            # Label styling
            tk.Label(
                left_frame,
                text=label,
                font=("Helvetica", 11, "bold"),
                bg="white",
                fg="#2C3E50"  # Dark blue-grey text
            ).grid(row=0, column=i*2, padx=5, pady=5)
            
            # Entry frame for border effect
            entry_frame = tk.Frame(
                left_frame,
                bg="#E0E7FF",  # Border color
                padx=1,
                pady=1
            )
            entry_frame.grid(row=0, column=i*2+1, padx=5, pady=5)
            
            # Entry widget with custom style
            entry = tk.Entry(
                entry_frame,
                textvariable=var,
                width=25 if i == 0 else 15,  # Product name entry wider
                **entry_style
            )
            entry.pack(ipady=5)  # Add vertical padding inside entry

            # Bind focus events for highlight effect
            entry.bind("<FocusIn>", lambda e, ef=entry_frame: ef.configure(bg="#3498DB"))
            entry.bind("<FocusOut>", lambda e, ef=entry_frame: ef.configure(bg="#E0E7FF"))

        # Right frame for buttons
        right_frame = tk.Frame(details_frame, bg="white")
        right_frame.pack(side=tk.RIGHT, padx=20, pady=5)

        # Button style
        button_style = {
            "font": ("Helvetica", 10, "bold"),
            "width": 8,
            "height": 1,
            "relief": "flat",
            "cursor": "hand2"
        }

        # Action Buttons with hover effect
        # Add Button
        btn_add = tk.Button(
            right_frame,
            text="Add",
            bg="#2ECC71",  # Green
            fg="white",
            activebackground="#27AE60",
            activeforeground="white",
            command=self.add_new_product,  # Add-specific command
            **button_style
        )
        btn_add.pack(side=tk.LEFT, padx=3)
        btn_add.bind("<Enter>", lambda e, b=btn_add: b.configure(bg="#27AE60"))
        btn_add.bind("<Leave>", lambda e, b=btn_add: b.configure(bg="#2ECC71"))

        # Update Button
        btn_update = tk.Button(
            right_frame,
            text="Update",
            bg="#3498DB",  # Blue
            fg="white",
            activebackground="#2980B9",
            activeforeground="white",
            command=self.update_product,  # Update-specific command
            **button_style
        )
        btn_update.pack(side=tk.LEFT, padx=3)
        btn_update.bind("<Enter>", lambda e, b=btn_update: b.configure(bg="#2980B9"))
        btn_update.bind("<Leave>", lambda e, b=btn_update: b.configure(bg="#3498DB"))

        # Delete Button
        btn_delete = tk.Button(
            right_frame,
            text="Delete",
            bg="#E74C3C",  # Red
            fg="white",
            activebackground="#C0392B",
            activeforeground="white",
            command=self.delete_product,  # Delete-specific command
            **button_style
        )
        btn_delete.pack(side=tk.LEFT, padx=3)
        btn_delete.bind("<Enter>", lambda e, b=btn_delete: b.configure(bg="#C0392B"))
        btn_delete.bind("<Leave>", lambda e, b=btn_delete: b.configure(bg="#E74C3C"))

        # Clear Button
        btn_clear = tk.Button(
            right_frame,
            text="Clear",
            bg="#95A5A6",  # Grey
            fg="white",
            activebackground="#7F8C8D",
            activeforeground="white",
            command=self.clear_fields,  # Clear-specific command
            **button_style
        )
        btn_clear.pack(side=tk.LEFT, padx=3)
        btn_clear.bind("<Enter>", lambda e, b=btn_clear: b.configure(bg="#7F8C8D"))
        btn_clear.bind("<Leave>", lambda e, b=btn_clear: b.configure(bg="#95A5A6"))


        # Table Frame
        table_frame = tk.Frame(self.products_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbars
        scroll_x = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scroll_y = tk.Scrollbar(table_frame, orient=tk.VERTICAL)
        
        # Products Table
        self.product_table = ttk.Treeview(
            table_frame,
            columns=("pid", "name", "price", "qty"),
            xscrollcommand=scroll_x.set,
            yscrollcommand=scroll_y.set
        )

        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.config(command=self.product_table.xview)
        scroll_y.config(command=self.product_table.yview)

        # Configure columns
        columns = {
            "pid": "Product ID",
            "name": "Name",
            "price": "Price",
            "qty": "Quantity",
        }

        for col, heading in columns.items():
            self.product_table.heading(col, text=heading)
            self.product_table.column(col, width=100)

        self.product_table["show"] = "headings"
        self.product_table.pack(fill=tk.BOTH, expand=True)
        self.product_table.bind("<ButtonRelease-1>", self.populate_fields)

        # Load initial products
        self.display_products()



    def setup_users_interface(self):
        """Create the user management interface"""
        # Title Frame
        title_frame = Frame(self.user_frame, bg="#1a237e")
        title_frame.pack(fill=X)
        
        title = Label(
            title_frame,
            text="User Management",
            font=("Helvetica", 20, "bold"),
            bg="#1a237e",
            fg="white",
            pady=10
        )
        title.pack()

        # Search Frame
        search_frame = LabelFrame(
            self.user_frame,
            text="Search Users",
            font=("Helvetica", 12, "bold"),
            bg="white",
            pady=15,
            padx=15,
            relief="groove"
        )
        search_frame.pack(fill=X, padx=10, pady=10)

        # Search Type Label and Dropdown
        Label(
            search_frame,
            text="Search By:",
            font=("Helvetica", 11, "bold"),
            bg="white",
            fg="#2C3E50"
        ).pack(side=LEFT, padx=5)

        search_combo = ttk.Combobox(
            search_frame,
            textvariable=self.var_user_searchtype,
            values=("Select", "Username", "Email", "Role"),
            state="readonly",
            width=15
        )
        search_combo.pack(side=LEFT, padx=5)
        search_combo.current(0)

        # Search Entry
        entry_frame = Frame(search_frame, bg="#E0E7FF", padx=1, pady=1)
        entry_frame.pack(side=LEFT, padx=10)

        search_entry = Entry(
            entry_frame,
            textvariable=self.var_user_search,
            font=("Helvetica", 11),
            bg="#F7F9FC",
            fg="#2C3E50",
            relief="flat",
            width=25
        )
        search_entry.pack(ipady=5)

        # Search and Clear Buttons
        btn_search = Button(
            search_frame,
            text="Search",
            command=self.search_users,
            bg="#3498DB",
            fg="white",
            font=("Helvetica", 10, "bold"),
            relief="flat",
            cursor="hand2"
        )
        btn_search.pack(side=LEFT, padx=5)

        btn_clear = Button(
            search_frame,
            text="Clear",
            command=self.clear_user_fields,
            bg="#95A5A6",
            fg="white",
            font=("Helvetica", 10, "bold"),
            relief="flat",
            cursor="hand2"
        )
        btn_clear.pack(side=LEFT, padx=5)

        # User Details Frame
        details_frame = LabelFrame(
            self.user_frame,
            text="User Details",
            font=("Helvetica", 12, "bold"),
            bg="white",
            pady=20,  # Increased padding
            padx=20,
            relief="groove"
        )
        details_frame.pack(fill=X, padx=20, pady=15)  # Increased outer padding

        # Create a container frame for fields with more width
        fields_frame = Frame(details_frame, bg="white")
        fields_frame.pack(pady=15, padx=30)  # Added horizontal padding

        # Style for entry boxes
        entry_style = {
            "font": ("Helvetica", 11),
            "bg": "#F8F9FA",
            "fg": "#2C3E50",
            "relief": "flat",
            "highlightthickness": 1,
            "highlightbackground": "#E0E7FF",
            "highlightcolor": "#3498DB",
            "insertbackground": "#2C3E50"
        }

        # Label style
        label_style = {
            "font": ("Helvetica", 11, "bold"),
            "bg": "white",
            "fg": "#2C3E50",
            "width": 10,  # Fixed width for labels
            "anchor": "e"  # Right-align text
        }

        # Username Field Container
        username_container = Frame(fields_frame, bg="white")
        username_container.pack(side=LEFT, padx=20)
        
        Label(
            username_container,
            text="Username :",
            **label_style
        ).pack(side=LEFT)

        username_entry = Entry(
            username_container,
            textvariable=self.var_username,
            width=15,  # Adjusted width
            **entry_style
        )
        username_entry.pack(side=LEFT, ipady=8)

        # Password Field Container
        password_container = Frame(fields_frame, bg="white")
        password_container.pack(side=LEFT, padx=20)
        
        Label(
            password_container,
            text="Password :",
            **label_style
        ).pack(side=LEFT)

        password_entry = Entry(
            password_container,
            textvariable=self.var_password,
            show="•",
            width=15,  # Adjusted width
            **entry_style
        )
        password_entry.pack(side=LEFT, ipady=8)

        # Email Field Container
        email_container = Frame(fields_frame, bg="white")
        email_container.pack(side=LEFT, padx=20)
        
        Label(
            email_container,
            text="Email :",
            **label_style
        ).pack(side=LEFT)

        email_entry = Entry(
            email_container,
            textvariable=self.var_email,
            width=20,  # Slightly wider for email
            **entry_style
        )
        email_entry.pack(side=LEFT, ipady=8)

        # Role Field Container
        role_container = Frame(fields_frame, bg="white")
        role_container.pack(side=LEFT, padx=20)
        
        Label(
            role_container,
            text="Role :",
            **label_style
        ).pack(side=LEFT)

        # Custom style for combobox
        style = ttk.Style()
        style.configure(
            "Custom.TCombobox",
            background="#F8F9FA",
            fieldbackground="#F8F9FA",
            selectbackground="#3498DB",
            selectforeground="white",
            padding=8
        )

        role_combo = ttk.Combobox(
            role_container,
            textvariable=self.var_user_role,
            values=["Admin", "User"],
            state="readonly",
            width=13,  # Adjusted width
            style="Custom.TCombobox"
        )
        role_combo.pack(side=LEFT)
        role_combo.set("Select Role")  # Default text

        # Buttons Frame - Centered
        btn_frame = Frame(details_frame, bg="white")
        btn_frame.pack(pady=25)  # Increased spacing

        # Button style
        button_style = {
            "font": ("Helvetica", 11, "bold"),
            "width": 8,  # Slightly smaller width
            "relief": "flat",
            "cursor": "hand2",
            "pady": 6,  # Slightly reduced padding
            "padx": 15  # Added horizontal padding
        }

        # Add button
        add_btn = Button(
            btn_frame,
            text="Add",
            command=self.add_user,
            bg="#2ECC71",
            fg="white",
            activebackground="#27AE60",
            activeforeground="white",
            **button_style
        )
        add_btn.pack(side=LEFT, padx=12)  # Increased spacing between buttons

        # Update button
        update_btn = Button(
            btn_frame,
            text="Update",
            command=self.update_user,
            bg="#3498DB",
            fg="white",
            activebackground="#2980B9",
            activeforeground="white",
            **button_style
        )
        update_btn.pack(side=LEFT, padx=12)

        # Delete button
        delete_btn = Button(
            btn_frame,
            text="Delete",
            command=self.delete_user,
            bg="#E74C3C",
            fg="white",
            activebackground="#C0392B",
            activeforeground="white",
            **button_style
        )
        delete_btn.pack(side=LEFT, padx=12)

        # Clear button
        clear_btn = Button(
            btn_frame,
            text="Clear",
            command=self.clear_user_fields,
            bg="#95A5A6",
            fg="white",
            activebackground="#7F8C8D",
            activeforeground="white",
            **button_style
        )
        clear_btn.pack(side=LEFT, padx=12)

        # Add hover effects for buttons
        def btn_hover_enter(e):
            if e.widget['bg'] == "#2ECC71":
                e.widget.configure(bg="#27AE60")
            elif e.widget['bg'] == "#3498DB":
                e.widget.configure(bg="#2980B9")
            elif e.widget['bg'] == "#E74C3C":
                e.widget.configure(bg="#C0392B")
            elif e.widget['bg'] == "#95A5A6":
                e.widget.configure(bg="#7F8C8D")

        def btn_hover_leave(e):
            if e.widget['bg'] == "#27AE60":
                e.widget.configure(bg="#2ECC71")
            elif e.widget['bg'] == "#2980B9":
                e.widget.configure(bg="#3498DB")
            elif e.widget['bg'] == "#C0392B":
                e.widget.configure(bg="#E74C3C")
            elif e.widget['bg'] == "#7F8C8D":
                e.widget.configure(bg="#95A5A6")

        # Bind hover effects to buttons
        for btn in [add_btn, update_btn, delete_btn, clear_btn]:
            btn.bind("<Enter>", btn_hover_enter)
            btn.bind("<Leave>", btn_hover_leave)

        # Users Table
        table_frame = Frame(self.user_frame)
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        scrollx = Scrollbar(table_frame, orient=HORIZONTAL)
        scrolly = Scrollbar(table_frame, orient=VERTICAL)

        self.users_table = ttk.Treeview(
            table_frame,
            columns=("username", "password", "email", "role", "last_login", "status"),
            xscrollcommand=scrollx.set,
            yscrollcommand=scrolly.set
        )

        scrollx.pack(side=BOTTOM, fill=X)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.config(command=self.users_table.xview)
        scrolly.config(command=self.users_table.yview)

        # Configure columns
        columns = {
            "username": ("Username", 150),
            "password": ("Password", 150),
            "email": ("Email", 200),
            "role": ("Role", 100),
            "last_login": ("Last Login", 150),
            "status": ("Status", 100)
        }

        for col, (heading, width) in columns.items():
            self.users_table.heading(col, text=heading)
            self.users_table.column(col, width=width)

        self.users_table["show"] = "headings"
        self.users_table.pack(fill=BOTH, expand=True)
        self.users_table.bind("<ButtonRelease-1>", self.get_user_data)

        # Load initial users
        self.display_users()



    def display_users(self):
        """Fetch and display users from the database with structure validation"""
        try:
            # Validate employee structure
            employees_ref = self.db.collection('Employee').document('Employee-List')
            doc = employees_ref.get()
            
            if not doc.exists:
                # Create initial structure if it doesn't exist
                employees_ref.set({'Employees': []})
                logging.info("Created initial Employee-List structure")
            
            # Clear existing table entries
            self.users_table.delete(*self.users_table.get_children())

            # Fetch employees
            doc = employees_ref.get()  # Refresh after potential creation
            data = doc.to_dict()
            employees = data.get('Employees', [])

            for emp in employees:
                # Display masked password
                masked_password = "••••••••" if emp.get('UserPassword') else ""
                
                self.users_table.insert('', 'end', values=(
                    emp.get('UserName', ''),
                    masked_password,
                    emp.get('UserEmail', ''),
                    emp.get('UserType', 'Admin'),  # Changed from 'admin' to 'Admin'
                    emp.get('LastLogin', 'Never'),
                    emp.get('UserStatus', 'Active')
                ))

        except Exception as e:
            logging.error(f"Error displaying users: {str(e)}")
            messagebox.showerror("Error", f"Error fetching users: {str(e)}")


    def add_user(self):
        """Add new user with proper validation"""
        try:
            # Validate inputs
            if not all([self.var_username.get(), self.var_password.get(), 
                       self.var_email.get(), self.var_user_role.get()]):
                messagebox.showerror("Error", "All fields are required!")
                return

            # Get current employees
            doc = self.db.collection('Employee').document('Employee-List').get()
            
            if not doc.exists:
                current_employees = []
            else:
                current_employees = doc.to_dict().get('Employees', [])

            # Check if username already exists
            if any(emp.get('UserName') == self.var_username.get() for emp in current_employees):
                messagebox.showerror("Error", "Username already exists!")
                return

            # Create new employee record
            new_employee = {
                "UserName": self.var_username.get(),
                "UserPassword": self.var_password.get(),
                "UserEmail": self.var_email.get(),
                "UserType": self.var_user_role.get(),
                "UserStatus": "Active",
                "LastLogin": "Never",
                "CreatedAt": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Add to employees list
            current_employees.append(new_employee)

            # Update Firestore
            self.db.collection('Employee').document('Employee-List').set(
                {"Employees": current_employees}
            )

            messagebox.showinfo("Success", "User added successfully!")
            self.clear_user_fields()
            self.display_users()

        except Exception as e:
            logging.error(f"Error adding user: {str(e)}")
            messagebox.showerror("Error", f"Failed to add user: {str(e)}")

    def update_user(self):
        try:
            # Get selected item
            selected = self.users_table.selection()
            if not selected:
                messagebox.showerror("Error", "Please select a user to update")
                return

            # Validate inputs
            if not all([self.var_username.get(), self.var_email.get(), 
                       self.var_user_role.get()]):
                messagebox.showerror("Error", "Required fields cannot be empty!")
                return

            # Get current employees
            doc = self.db.collection('Employee').document('Employee-List').get()
            if not doc.exists:
                messagebox.showerror("Error", "No users found")
                return

            employees = doc.to_dict().get('Employees', [])

            # Find and update user
            updated = False
            for emp in employees:
                if emp.get('UserName') == self.var_username.get():
                    # Update fields
                    emp['UserEmail'] = self.var_email.get()
                    emp['UserType'] = self.var_user_role.get()
                    if self.var_password.get():  # Update password only if provided
                        emp['UserPassword'] = self.var_password.get()
                    updated = True
                    break

            if not updated:
                messagebox.showerror("Error", "User not found")
                return

            # Update Firestore
            self.db.collection('Employee').document('Employee-List').set(
                {"Employees": employees}
            )

            messagebox.showinfo("Success", "User updated successfully!")
            self.clear_user_fields()
            self.display_users()

        except Exception as e:
            logging.error(f"Error updating user: {str(e)}")
            messagebox.showerror("Error", f"Failed to update user: {str(e)}")

    def delete_user(self):
        """Delete selected user"""
        try:
            # Get selected item
            selected = self.users_table.selection()
            if not selected:
                messagebox.showerror("Error", "Please select a user to delete")
                return

            # Confirm deletion
            if not messagebox.askyesno("Confirm", "Do you want to delete this user?"):
                return

            # Get username from selected item
            username = self.users_table.item(selected)['values'][0]

            # Get current employees
            doc = self.db.collection('Employee').document('Employee-List').get()
            if not doc.exists:
                messagebox.showerror("Error", "No users found")
                return

            employees = doc.to_dict().get('Employees', [])

            # Remove user
            employees = [emp for emp in employees if emp.get('UserName') != username]

            # Update Firestore
            self.db.collection('Employee').document('Employee-List').set(
                {"Employees": employees}
            )

            messagebox.showinfo("Success", "User deleted successfully!")
            self.clear_user_fields()
            self.display_users()

        except Exception as e:
            logging.error(f"Error deleting user: {str(e)}")
            messagebox.showerror("Error", f"Failed to delete user: {str(e)}")

    def get_user_data(self, ev):
        try:
            selected_row = self.users_table.focus()
            contents = self.users_table.item(selected_row)
            row = contents['values']
            
            if row:
                self.var_username.set(row[0])
                self.var_password.set("")  # Don't show password
                self.var_email.set(row[2])
                self.var_user_role.set(row[3])
        except Exception as e:
            logging.error(f"Error getting user data: {str(e)}")
            messagebox.showerror("Error", f"Error getting user data: {str(e)}")

    def clear_user_fields(self):
        """Clear all user input fields and refresh table"""
        try:
            # Clear all input fields
            self.var_username.set("")
            self.var_password.set("")
            self.var_email.set("")
            self.var_user_role.set("Select Role")  # Reset to default
            self.var_user_search.set("")
            self.var_user_searchtype.set("Select")

            # Clear any table selection
            if hasattr(self, 'users_table'):
                self.users_table.selection_remove(*self.users_table.selection())

            # Refresh table to show all data
            self.display_users()

            logging.info("User fields cleared and table refreshed")

        except Exception as e:
            logging.error(f"Error clearing user fields: {str(e)}")
            messagebox.showerror("Error", f"Error clearing fields: {str(e)}")

    def search_users(self):
        """Search users based on selected criteria"""
        try:
            if self.var_user_searchtype.get() == "Select":
                messagebox.showerror("Error", "Please select search criteria")
                return
            
            search_term = self.var_user_search.get()
            if not search_term:
                messagebox.showerror("Error", "Please enter search term")
                return

            # Clear current table
            self.users_table.delete(*self.users_table.get_children())
            
            # Get Employee-List document
            doc = self.db.collection('Employee').document('Employee-List').get()
            
            if not doc.exists:
                messagebox.showinfo("Info", "No users found")
                return
                
            # Get employees list
            employees = doc.to_dict().get('Employees', [])
            found = False
            
            # Map search type to employee field
            field_map = {
                "Username": "UserName",
                "Email": "UserEmail",
                "Role": "UserType"
            }
            
            search_field = field_map.get(self.var_user_searchtype.get())
            if not search_field:
                messagebox.showerror("Error", "Invalid search type")
                return
                
            # Search through employees
            for emp in employees:
                if search_field in emp:
                    field_value = str(emp[search_field]).lower()
                    if field_value.startswith(search_term.lower()):
                        found = True
                        self.users_table.insert('', 'end', values=(
                            emp.get('UserName', ''),
                            "••••••••",  # Masked password
                            emp.get('UserEmail', ''),
                            emp.get('UserType', 'User'),
                            emp.get('LastLogin', 'Never'),
                            emp.get('UserStatus', 'Active')
                        ))
            
            if not found:
                messagebox.showinfo("Info", "No matching users found")
                self.display_users()  # Show all users if no matches
                
        except Exception as e:
            logging.error(f"Error searching users: {str(e)}")
            messagebox.showerror("Error", f"Error searching users: {str(e)}")

    def create_hover_effect(self, widget, enter_color, leave_color):
        widget.bind('<Enter>', lambda e: widget.config(bg=enter_color))
        widget.bind('<Leave>', lambda e: widget.config(bg=leave_color))
