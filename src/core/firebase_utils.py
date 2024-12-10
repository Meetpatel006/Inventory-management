"""Firebase connection and initialization utilities"""
import os
from dotenv import load_dotenv
import logging
import time
import tkinter as messagebox

import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables from .env file
load_dotenv()

def setup_firebase():
    """Initialize Firebase connection with error handling"""
    try:
        try:
            return firebase_admin.get_app()
        except ValueError:
            
            # Create a credentials object from environment variables
            cred = credentials.Certificate({
                "type": os.getenv("FIREBASE_TYPE"),
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key":"-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCycdi7+61ZYtsZ\ntRkR8n/OJouaL8l/fwLHXmYpwaSaot5EqdSfMeAvavE+9KlmXVksE/eNDkQMOYrB\nLnfTjnu9R7GvN1CzbeVn3kn66FFZLSfUlkSFDXLrfrv4R/ug7q+ir0+/rAbnpYJ/\nf06TuTL9uy4PNYD5BIsvQHALbxkIoin4NBC7TKn0zVBqVroWi8G+uTK99k3aRwCs\n3zLi6JYSS84pFJPbl62mLYq52TrCNPGjhVtArnOLH+s1t5KuQDkT4ubpILFb7xbm\nGf/Z+z4NJPiUM3f+XvL/mzNkCUtScwr2oJW2n35Z2b73wjCtx29H0onntOtarPcm\nBdwlARNZAgMBAAECggEAIHYZaUkFZedX2DtbjipBGa1lY+0hiLIAPWhsyVfSq9bI\n/FCwvy0BjV60+DDlyBtfJ2eSdvSLaHXnSfE8Fx4qYGp0Zl13rsxlGRoU9zHf6osO\nXdvgJxwlNbXeV/IwUjxZcwzVQxb2QpmXPb5Y+wKLxiCQ5m9jQOmUsEnWmB3jvfAD\nlAPCtUfcg7TQHsgtiNNQrXOdPu/xHJEGr7jC13BDBNNwO8oQNc8dgKtfhfUOhLNF\nd9a165SB2u7Cyz6YFYTwVHCQhz6KDG/dRD0+NU7Hn/gUe95c/JBUDiEn9cS9k2nt\nY50Rr8cGyRzfjCbQ0m1ONvVr3uaLeiiGjLWjfKJWCQKBgQD1fGRkhykKp8sxXPOi\nKQs5pRMC9Iho7iV4K4d/FgYh/0eELW9isjrZc2ilc8JV1E8zi7xpMl6xENPgIFnI\nl0Ylixa/I2MLg1uDj45YT9pR33JDxXQkd/r+gbZ+LutOi8piJa01glZ04+eEZbC+\ngXq4KYhk/ONh1Uj7fuhWyaINEwKBgQC6FmMtD8t1exqEq7jOeAbrddj6Ab+peXZ0\nAQhIj3LI03J3F7m4W5SsWWbMFDeF2juWbhopRymiy7WGKoJDy7a9kff7dNnV4aPQ\nv5R93svpq+wSeTlcIx1Lv3IVYuHgmamLR4OlVC3BGBLwd5ASgYtcBkptUSZC3C8Z\n/Sy4MuuHYwKBgEAGupRxoCW0T83HJZAkzlWxlTzPFIjxm/o0uDlQQDc7wqZZx1Rh\nkfHHJQMKJySFpEaYaoKxbXsXHXu2VFR6CASgu0UM8Lc/Am5U0dZ8tT9nXQEKDdm5\nJVCd+j/88shgs19X3k43eV8xVd/1OdzmHmDMDFPylUed/lQB7I0+N7LbAoGAcsFh\nkaVe4+jxloVLZ1APfF7lWm9/oWR9DtagJBcKQxxaR2UDK9SWH57WTN3ey5WkD4WA\nbpoq6/DR1ZYbVPGolMkScyhBOat3WUD7so+VkllqMI4/ODmTVGYQVW3wO5CnRHPq\nlCcQPDa7Xz1sRG1M4ogil71mae7cwRsm28TTCF8CgYEAo9JXa6dxWWJ6cTzLYvyV\nOIFMZPY6G8kT1w17FjeY1ddvzmgAOZI0Omytm6GhwHh4OgUt4E88v/DgtKQCh2mQ\n6fLPZKc1//jOFp56uQ7IXEG1LUXJYcikLrwBUXMbfIfPSw7D/VxgWL+Fhh5/Go5M\nBCLhpvsZOIE/n/nwkwVOK9Q=\n-----END PRIVATE KEY-----\n",  # Ensure newlines are handled
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
                "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
                "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
                "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
                })
            firebase_admin.initialize_app(cred)
            logging.info("Firebase initialized successfully")
            return firebase_admin.get_app()
    except Exception as e:
        logging.error(f"Firebase initialization failed: {str(e)}")
        return None

def get_db_instance():
    """Get Firestore database instance"""
    try:
        return firestore.client()
    except Exception as e:
        logging.error(f"Failed to get Firestore instance: {str(e)}")
        return None
def connect_firebase():
    """Establish a connection to Firebase Firestore with retry logic"""
    max_retries = 3
    retry_delay = 2  # seconds
        
    for attempt in range(max_retries):
        try:
            if not hasattr(firebase_admin, '_apps') or not firebase_admin._apps:
                app = setup_firebase()
                if not app:
                    raise ConnectionError("Failed to initialize Firebase")
                    
            db = firestore.client()
                
            # Test connection
            db.collection('test').document('test').get()
            logging.info("Firebase connection established successfully")
            return db
                
        except Exception as e:
            logging.error(f"Firebase connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                messagebox.showerror(
                    "Connection Error",
                    "Failed to connect to database. Please check your internet connection."
                )
                return None

def check_firebase_connection():
    """Test Firebase connection and return status"""
    try:
        db = firestore.client()
        db.collection('test').document('test').get()
        return True
    except Exception as e:
        logging.error(f"Firebase connection test failed: {str(e)}")
        return False

