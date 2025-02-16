import firebase_admin
from firebase_admin import credentials, auth
from typing import Dict, Optional
import jwt
from datetime import datetime, timedelta

class FirebaseAuth:
    """Firebase Authentication Manager for the trading system."""
    
    def __init__(self):
        # Initialize Firebase Admin SDK
        try:
            cred = credentials.Certificate("path/to/serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
        except ValueError:
            # App already initialized
            pass
    
    async def register_user(self, email: str, password: str,
                           user_data: Dict) -> Dict:
        """Register a new user with Firebase."""
        try:
            # Create user in Firebase
            user = auth.create_user(
                email=email,
                password=password,
                display_name=user_data.get("name", ""),
                phone_number=user_data.get("phone", ""),
                email_verified=False
            )
            
            # Add custom claims for user role
            auth.set_custom_user_claims(
                user.uid,
                {
                    "role": user_data.get("role", "user"),
                    "trading_enabled": False,
                    "created_at": datetime.now().isoformat()
                }
            )
            
            return {
                "success": True,
                "user_id": user.uid,
                "email": user.email,
                "message": "User registered successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to register user"
            }
    
    async def login_user(self, email: str, password: str) -> Dict:
        """Login user and return custom token."""
        try:
            # Verify user exists
            user = auth.get_user_by_email(email)
            
            # Generate custom token
            custom_token = auth.create_custom_token(user.uid)
            
            # Get user claims
            user_claims = auth.get_user(user.uid).custom_claims or {}
            
            return {
                "success": True,
                "user_id": user.uid,
                "token": custom_token.decode(),
                "email": user.email,
                "role": user_claims.get("role", "user"),
                "trading_enabled": user_claims.get("trading_enabled", False),
                "message": "Login successful"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to login"
            }
    
    async def verify_token(self, token: str) -> Dict:
        """Verify Firebase token."""
        try:
            # Verify token
            decoded_token = auth.verify_id_token(token)
            
            # Get user data
            user = auth.get_user(decoded_token["uid"])
            
            return {
                "success": True,
                "user_id": user.uid,
                "email": user.email,
                "claims": decoded_token.get("claims", {}),
                "message": "Token verified"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Invalid token"
            }
    
    async def update_user(self, user_id: str, update_data: Dict) -> Dict:
        """Update user data in Firebase."""
        try:
            # Update user
            auth.update_user(
                user_id,
                email=update_data.get("email"),
                phone_number=update_data.get("phone"),
                email_verified=update_data.get("email_verified"),
                password=update_data.get("password"),
                display_name=update_data.get("name"),
                disabled=update_data.get("disabled", False)
            )
            
            # Update custom claims if provided
            if "claims" in update_data:
                auth.set_custom_user_claims(user_id, update_data["claims"])
            
            return {
                "success": True,
                "user_id": user_id,
                "message": "User updated successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update user"
            }
    
    async def delete_user(self, user_id: str) -> Dict:
        """Delete user from Firebase."""
        try:
            auth.delete_user(user_id)
            
            return {
                "success": True,
                "message": "User deleted successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to delete user"
            }
    
    async def enable_trading(self, user_id: str) -> Dict:
        """Enable trading for a user."""
        try:
            # Get current claims
            user = auth.get_user(user_id)
            current_claims = user.custom_claims or {}
            
            # Update claims
            current_claims["trading_enabled"] = True
            current_claims["trading_enabled_at"] = datetime.now().isoformat()
            
            # Set new claims
            auth.set_custom_user_claims(user_id, current_claims)
            
            return {
                "success": True,
                "user_id": user_id,
                "message": "Trading enabled successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to enable trading"
            }
    
    async def disable_trading(self, user_id: str, reason: str = "") -> Dict:
        """Disable trading for a user."""
        try:
            # Get current claims
            user = auth.get_user(user_id)
            current_claims = user.custom_claims or {}
            
            # Update claims
            current_claims["trading_enabled"] = False
            current_claims["trading_disabled_at"] = datetime.now().isoformat()
            current_claims["trading_disabled_reason"] = reason
            
            # Set new claims
            auth.set_custom_user_claims(user_id, current_claims)
            
            return {
                "success": True,
                "user_id": user_id,
                "message": "Trading disabled successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to disable trading"
            }
    
    async def get_user_data(self, user_id: str) -> Dict:
        """Get user data from Firebase."""
        try:
            user = auth.get_user(user_id)
            claims = user.custom_claims or {}
            
            return {
                "success": True,
                "user_id": user.uid,
                "email": user.email,
                "name": user.display_name,
                "phone": user.phone_number,
                "email_verified": user.email_verified,
                "role": claims.get("role", "user"),
                "trading_enabled": claims.get("trading_enabled", False),
                "created_at": claims.get("created_at"),
                "message": "User data retrieved successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get user data"
            }
