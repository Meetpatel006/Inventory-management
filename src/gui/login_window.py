"""
Login window GUI module.
"""
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import logging
import pickle
import os

from .admin_window import AdminIMS
from .user_window import UserIMS
from datetime import datetime
from src.core.admin_functions import login_authenticate_user, setup_firebase

class LoginWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Inventory Management System")
        self.window.geometry("1000x600")
        self.window.configure(bg="#f0f0f0")
        
        # Initialize variables
        self.var_username = tk.StringVar()
        self.var_password = tk.StringVar()
        self.var_user_type = tk.StringVar(value="normal")
        self.remember_me = tk.BooleanVar()  # Variable for Remember Me checkbox
        
        # Initialize Firebase
        setup_firebase()  # Use the centralized setup function
        
        # Create credentials directory if it doesn't exist
        self.credentials_dir = "config/credentials"
        os.makedirs(self.credentials_dir, exist_ok=True)

        # Create interface FIRST
        self.create_login_interface()
        # THEN load credentials
        self.load_credentials()

    def create_login_interface(self):
        # Define modern color scheme
        COLORS = {
            'bg': "#F7F8FA",           # Light grayish background
            'primary': "#4A90E2",      # Soft blue
            'text': "#333333",         # Darker text
            'placeholder': "#B0B3B8",  # Placeholder text
            'border': "#D1D5DB",       # Light gray border
            'input_bg': "#FFFFFF",     # White for input boxes
            'button_hover': "#357ABD"  # Darker blue for hover
        }

        # Configure the main window
        self.window.configure(bg=COLORS['bg'])

        # Main container frame
        container = tk.Frame(self.window, bg=COLORS['bg'])
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        tk.Label(
            container,
            text="IMS",
            font=("Arial", 36, "bold"),
            bg=COLORS['bg'],
            fg=COLORS['primary']
        ).pack(pady=(0, 10))

        # Subtitle
        tk.Label(
            container,
            text="Welcome Back",
            font=("Arial", 20, "bold"),
            bg=COLORS['bg'],
            fg=COLORS['text']
        ).pack()

        tk.Label(
            container,
            text="Please enter your credentials to continue",
            font=("Arial", 12),
            bg=COLORS['bg'],
            fg=COLORS['placeholder']
        ).pack(pady=(5, 20))

        # User Type Dropdown
        tk.Label(
            container,
            text="User Type",
            font=("Arial", 12, "bold"),
            bg=COLORS['bg'],
            fg=COLORS['text']
        ).pack(anchor="w", padx=10, pady=(0, 5))

        # Create a style for the Combobox
        style = ttk.Style()
        style.configure("Custom.TCombobox",
                        background=COLORS['input_bg'],
                        foreground=COLORS['text'],
                        arrowcolor=COLORS['primary'])

        self.user_type = ttk.Combobox(
            container,
            values=["Admin", "User"],
            state="readonly",
            font=("Arial", 12),
            style="Custom.TCombobox"
        )
        self.user_type.set("Select User Type")
        self.user_type.pack(pady=(0, 20), padx=10, fill="x")

        # Bind the selection event to load credentials
        self.user_type.bind("<<ComboboxSelected>>", self.load_credentials)

        # Username Entry
        self.create_modern_entry(container, "Enter your username", "Username")

        # Password Entry
        self.create_modern_entry(container, "Enter your password", "Password", show="*")

        # Remember Me Checkbox
        remember_me_checkbox = tk.Checkbutton(
            container,
            text="Remember Me",
            variable=self.remember_me,
            bg=COLORS['bg'],
            fg=COLORS['text'],
            font=("Arial", 12)
        )
        remember_me_checkbox.pack(anchor="w", padx=10, pady=(0, 20))

        # Login Button
        login_button = tk.Button(
            container,
            text="Login",
            font=("Arial", 14, "bold"),
            bg=COLORS['primary'],
            fg="#FFFFFF",
            relief="flat",
            command=self.handle_login,
            cursor="hand2",
            height=2
        )
        login_button.pack(pady=(30, 0), padx=20, fill="x")

        # Add hover effects for login button
        login_button.bind("<Enter>", lambda e: login_button.config(bg=COLORS['button_hover']))
        login_button.bind("<Leave>", lambda e: login_button.config(bg=COLORS['primary']))

        # Center window
        self.window.geometry("400x600")
        self.window.resizable(False, False)
        self.center_window()

    def create_modern_entry(self, parent, placeholder, label_text, show=None):
        """Creates a modern-looking entry with label and placeholder."""
        COLORS = {
            'text': "#333333",
            'placeholder': "#B0B3B8",
            'input_bg': "#FFFFFF",
            'border': "#D1D5DB"
        }

        # Label
        tk.Label(
            parent,
            text=label_text,
            font=("Arial", 12, "bold"),
            bg="#F7F8FA",
            fg=COLORS['text']
        ).pack(anchor="w", padx=10, pady=(0, 5))

        # Input frame
        input_frame = tk.Frame(parent, bg=COLORS['input_bg'], highlightbackground=COLORS['border'], highlightthickness=1)
        input_frame.pack(fill="x", padx=10, pady=(0, 20))

        # Entry box
        entry = tk.Entry(
            input_frame,
            font=("Arial", 12),
            bg=COLORS['input_bg'],
            fg=COLORS['placeholder'],
            relief="flat",
            bd=0,
            width=30,
            show=show
        )
        entry.insert(0, placeholder)
        entry.bind("<FocusIn>", lambda e: self.on_entry_focus(entry, placeholder, show))
        entry.bind("<FocusOut>", lambda e: self.on_entry_focus_out(entry, placeholder))
        entry.pack(fill="x", padx=5, pady=10)

        # Bind the entry to the appropriate variable
        if label_text == "Username":
            self.entry_1 = entry  # Store reference to username entry
        elif label_text == "Password":
            self.entry_2 = entry  # Store reference to password entry

        return entry

    def on_entry_focus(self, entry, placeholder, show):
        """Handle focus-in for entry boxes."""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="#333333", show=show)

    def on_entry_focus_out(self, entry, placeholder):
        """Handle focus-out for entry boxes."""
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg="#B0B3B8", show="")

    def center_window(self):
        """Centers the window on the screen."""
        window_width, window_height = 400, 600
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def handle_login(self):
        """Handle login with enhanced validation and routing"""
        try:
            username = self.entry_1.get().strip()  # Use the stored reference
            password = self.entry_2.get().strip()  # Use the stored reference
            user_type = self.user_type.get()
            
            # Add debug logging
            logging.info(f"Login attempt - Username: {username}, Type: {user_type}")
            
            # Validate all fields are filled
            if not username:
                messagebox.showerror("Error", "Please enter username")
                return
            if not password:
                messagebox.showerror("Error", "Please enter password")
                return
            if not user_type or user_type == "Select User Type":
                messagebox.showerror("Error", "Please select user type")
                return
            
            # Initialize Firebase if not already initialized
            setup_firebase()  # Use the centralized setup function
            
            # Use the modified login_authenticate_user function
            is_valid, result = login_authenticate_user(username, password, user_type)
            
            if is_valid:
                if self.remember_me.get():
                    # Remove password hashing and save plain password
                    self.save_credentials(username, password)  # Save plain password
                else:
                    self.clear_credentials()  # Clear saved credentials if not
                
                self.window.destroy()
                root = Tk()
                
                # Route to appropriate interface based on stored type
                if result.lower() == "admin":
                    obj = AdminIMS(root)
                else:  # User
                    obj = UserIMS(root)
                
                root.mainloop()
            else:
                # Show specific error messages based on result
                if result == "type_mismatch":
                    messagebox.showerror(
                        "Access Denied",
                        "Your account type does not match the selected user type.\nPlease select the correct user type."
                    )
                elif result == "invalid_credentials":
                    messagebox.showerror(
                        "Login Failed",
                        "Invalid username or password"
                    )
                else:
                    messagebox.showerror(
                        "Error",
                        "Login failed. Please try again."
                    )
                    
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Login failed: {str(e)}\nPlease try again."
            )

    def save_credentials(self, username, password):
        """Save credentials to a file in the credentials directory."""
        try:
            # Determine the file name based on user type
            user_type = self.user_type.get().lower()  # Get the selected user type
            credentials_path = os.path.join(self.credentials_dir, f"{user_type}_credentials.pkl")
            
            # Don't save if username is the placeholder
            if username == "Enter your username" or password == "Enter your password":
                return
                
            credentials = {
                'username': username,
                'password': password
            }
            
            with open(credentials_path, "wb") as f:
                pickle.dump(credentials, f)
            logging.info(f"{user_type.capitalize()} credentials saved successfully")
        except Exception as e:
            logging.error(f"Error saving {user_type} credentials: {str(e)}")


    def load_credentials(self, event=None):
        """Load credentials from a file if they exist."""
        user_type = self.user_type.get().lower()  # Get the selected user type
        credentials_path = os.path.join(self.credentials_dir, f"{user_type}_credentials.pkl")
        
        if os.path.exists(credentials_path):
            try:
                with open(credentials_path, "rb") as f:
                    credentials = pickle.load(f)
                    username = credentials.get('username', '')
                    password = credentials.get('password', '')
                    
                    if username and hasattr(self, 'entry_1'):
                        self.entry_1.delete(0, tk.END)
                        self.entry_1.insert(0, username)
                        self.entry_1.config(fg="#333333")  # Set to regular text color
                        # Clear the placeholder state
                        if self.entry_1.get() == "Enter your username":
                            self.entry_1.delete(0, tk.END)
                    
                    if password and hasattr(self, 'entry_2'):
                        self.entry_2.delete(0, tk.END)
                        self.entry_2.insert(0, password)
                        self.entry_2.config(fg="#333333", show="*")  # Set to regular text color and show as password
                        # Clear the placeholder state
                        if self.entry_2.get() == "Enter your password":
                            self.entry_2.delete(0, tk.END)
                    
                    self.remember_me.set(True)  # Check the Remember Me box
                    logging.info(f"{user_type.capitalize()} credentials loaded successfully")
            except Exception as e:
                logging.error(f"Error loading {user_type} credentials: {str(e)}")

    def clear_credentials(self):
        """Clear saved credentials."""
        credentials_path = os.path.join(self.credentials_dir, "credentials.pkl")
        if os.path.exists(credentials_path):
            os.remove(credentials_path)

