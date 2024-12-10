"""Authentication related functions"""
import logging
from datetime import datetime
from firebase_admin import firestore
from .firebase_utils import get_db_instance

def login_authenticate_user(username, password, user_type):
    """Authenticate user with Firebase and return their type if valid"""
    try:
        db = get_db_instance()
        if not db:
            return False, "error"

        doc = db.collection('Employee').document('Employee-List').get()
        employees = doc.to_dict().get('Employees', [])

        for emp in employees:
            if (emp.get('UserName') == username and 
                emp.get('UserPassword') == password and 
                emp.get('UserType').lower() == user_type.lower()):
                
                # Update last login
                update_last_login(db, username)
                return True, emp.get('UserType')

        return False, "invalid_credentials"
    except Exception as e:
        logging.error(f"Authentication failed: {str(e)}")
        return False, "error"

def update_last_login(db, username):
    """Update user's last login timestamp"""
    try:
        doc_ref = db.collection('Employee').document('Employee-List')
        doc = doc_ref.get()
        employees = doc.to_dict().get('Employees', [])
        
        for emp in employees:
            if emp.get('UserName') == username:
                emp['LastLogin'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                doc_ref.update({'Employees': employees})
                break
    except Exception as e:
        logging.error(f"Failed to update last login: {str(e)}")
