"""User management functions"""
import logging
from datetime import datetime
from .firebase_utils import get_db_instance

def create_user(username, password, email, role):
    """Create new user in database"""
    try:
        db = get_db_instance()
        doc_ref = db.collection('Employee').document('Employee-List')
        doc = doc_ref.get()
        employees = doc.to_dict().get('Employees', [])
        
        # Check if username exists
        if any(emp.get('UserName') == username for emp in employees):
            return False, "Username already exists"
            
        new_employee = {
            "UserName": username,
            "UserPassword": password,
            "UserEmail": email,
            "UserType": role,
            "UserStatus": "Active",
            "LastLogin": "Never",
            "CreatedAt": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        employees.append(new_employee)
        doc_ref.set({"Employees": employees})
        return True, "User created successfully"
    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")
        return False, str(e)

def fetch_users():
    """Fetch all users from database"""
    try:
        db = get_db_instance()
        doc = db.collection('Employee').document('Employee-List').get()
        return doc.to_dict().get('Employees', [])
    except Exception as e:
        logging.error(f"Error fetching users: {str(e)}")
        return []

