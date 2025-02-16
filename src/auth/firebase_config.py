import os
import json
import firebase_admin
from firebase_admin import credentials, auth

def init_firebase():
    """Initialize Firebase with credentials from environment variables."""
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": os.getenv('FIREBASE_PROJECT_ID'),
        "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
        "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
        "token_uri": "https://oauth2.googleapis.com/token"
    })
    try:
        firebase_admin.initialize_app(cred)
        return True
    except Exception as e:
        print(f"Firebase initialization error: {str(e)}")
        return False

def verify_token(token):
    """Verify Firebase ID token."""
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        return None
