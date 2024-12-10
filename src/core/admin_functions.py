"""
Admin functionality module for the Inventory Management System.
Contains functions for user management, product management, and system initialization.
"""
import os
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
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


# Firebase initialization and connection functions
def setup_firebase():
    """Initialize Firebase connection with error handling"""
    try:
        try:
            return firebase_admin.get_app()
        except ValueError: 
            firebase_admin.initialize_app(cred)
            logging.info(f"Firebase initialized successfully using credentials from : .env ")
            return firebase_admin.get_app()
    except Exception as e:
        logging.error(f"Firebase initialization failed: {str(e)}")
        return None

def check_firebase_connection():
    """Test Firebase connection and return status"""
    try:
        db = firestore.client()
        db.collection('test').document('test').get()
        logging.info("Firebase connection established successfully")
        return True
    except Exception as e:
        logging.error(f"Firebase connection test failed: {str(e)}")
        return False

# User Management Functions
def get_employees_list():
    """Fetch all employees from database"""
    try:
        db = firestore.client()
        # Update the reference to use correct collection and document
        employees_ref = db.collection("Employee").document("Employee-List")
        doc = employees_ref.get()
        if not doc.exists:
            logging.warning("Employees document not found")
            return []
        data = doc.to_dict()
        if not data or 'Employees' not in data:
            logging.warning("No employees data found")
            return []
        return data.get('Employees', [])
    except Exception as e:
        logging.error(f"Error in get_employees_list: {e}")
        return []

def login_authenticate_user(username, password, user_type):
    """Authenticate user with username, password and user type"""
    try:
        if not all([username, password, user_type]):
            raise ValueError("All fields are required")
            
        employees = get_employees_list()
        input_username = username.lower()
        
        for emp in employees:
            # Make case-insensitive comparison for username
            stored_username = emp.get('UserName', '').lower()
            stored_type = emp.get('UserType', '')
            
            # Debug logging
            logging.info(f"Comparing - Stored: {stored_username}, Input: {input_username}")
            logging.info(f"User Types - Stored: {stored_type}, Input: {user_type}")
            
            if stored_username == input_username and emp.get('UserPassword') == password:
                # Case-insensitive comparison for user type
                if stored_type.lower() == user_type.lower():
                    try:
                        # Update LastLogin time
                        db = firestore.client()
                        employees_ref = db.collection("Employee").document("Employee-List")
                        employees_data = employees_ref.get().to_dict()
                        employees_list = employees_data.get('Employees', [])
                        
                        # Find and update the matching employee
                        for emp_record in employees_list:
                            if emp_record.get('UserName', '').lower() == input_username:
                                emp_record['LastLogin'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                break
                                
                        # Update the document
                        employees_ref.set({'Employees': employees_list})
                        logging.info(f"Login successful for user: {username}")
                        
                    except Exception as e:
                        logging.error(f"Failed to update LastLogin: {e}")
                    
                    return True, stored_type  # Return the stored type to maintain proper case
                else:
                    logging.warning(f"User type mismatch - User: {username}, Expected: {stored_type}, Got: {user_type}")
                    return False, "type_mismatch"
        
        # Log failed attempt with more details
        logging.warning(f"Failed login attempt - Username: {username}, Type: {user_type}")
        logging.warning("Available users: " + ", ".join([emp.get('UserName', '') for emp in employees]))
        return False, "invalid_credentials"
        
    except Exception as e:
        logging.error(f"Error in login_authenticate_user: {e}")
        return False, "error"

def add_user(username, password, email, user_role):
    """Add new user with proper validation"""
    try:
        # Validate inputs
        if not all([username, password, email, user_role]):
            raise ValueError("All fields are required!")

        # Get current employees
        doc = firestore.client().collection('Employee').document('Employee-List').get()
        
        if not doc.exists:
            current_employees = []
        else:
            current_employees = doc.to_dict().get('Employees', [])

        # Check if username already exists
        if any(emp.get('UserName') == username for emp in current_employees):
            raise ValueError("Username already exists!")

        # Create new employee record
        new_employee = {
            "UserName": username,
            "UserPassword": password,
            "UserEmail": email,
            "UserType": user_role,
            "UserStatus": "Active",
            "LastLogin": "Never",
            "CreatedAt": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Add to employees list
        current_employees.append(new_employee)

        # Update Firestore
        firestore.client().collection('Employee').document('Employee-List').set(
            {"Employees": current_employees}
        )

        return True, "User added successfully!"

    except Exception as e:
        logging.error(f"Error adding user: {str(e)}")
        return False, f"Failed to add user: {str(e)}"

# Product Management Functions
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
            return []
            
        products = doc.to_dict().get('Products', [])
        
        if products is None:
            logging.warning("No products found in the document")
            return []  # Return an empty list if no products are found
            
        logging.info(f"Successfully fetched {len(products)} products")
        return products
        
    except Exception as e:
        logging.error(f"Error fetching products: {str(e)}")
        return []

def create_product(name, price, quantity):
    """Create new product in database"""
    try:
        db = firestore.client()
        products_ref = db.collection('All-Products').document('Products-List')
        
        # Get existing products
        doc = products_ref.get()
        existing_products = doc.to_dict().get('Products', []) if doc.exists else []
        
        # Generate new PID
        pid = f"P{str(len(existing_products) + 1).zfill(3)}"
        
        # Create product data
        product_data = {
            "PID": pid,
            "Name": name,
            "Price": float(price),
            "QTY": int(quantity)
        }
        
        # Add to existing products
        existing_products.append(product_data)
        products_ref.set({'Products': existing_products}, merge=True)
        
        logging.info(f"Successfully created product: {name} (ID: {pid})")
        return True
        
    except Exception as e:
        logging.error(f"Error creating product: {str(e)}")
        return False
