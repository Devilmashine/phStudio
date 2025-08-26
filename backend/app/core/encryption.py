"""
Cost-effective encryption service for phStudio.
Uses Python standard library for zero additional dependency cost.
Provides field-level encryption for sensitive client data.
"""

import hashlib
import hmac
import secrets
import base64
import json
from datetime import datetime
from typing import Optional, Dict, Any, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging
import os

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Field-level encryption service for sensitive data.
    Uses Fernet (AES 128 in CBC mode) for symmetric encryption.
    Cost-effective solution using only cryptography library.
    """
    
    def __init__(self, master_key: Optional[str] = None):
        self.master_key = master_key or self._get_master_key()
        self._key_cache = {}
        
    def _get_master_key(self) -> str:
        """Get or generate master encryption key"""
        # In production, this should come from environment variable or key management service
        master_key = os.getenv("ENCRYPTION_MASTER_KEY")
        if not master_key:
            # Generate a new key if none exists (development only)
            master_key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
            logger.warning("Generated new master key. Set ENCRYPTION_MASTER_KEY environment variable in production!")
        return master_key
    
    def _derive_key(self, context: str, salt: Optional[bytes] = None) -> Fernet:
        """Derive encryption key for specific context"""
        if context in self._key_cache:
            return self._key_cache[context]
        
        if salt is None:
            salt = hashlib.sha256(context.encode()).digest()[:16]
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # OWASP recommended minimum
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        fernet = Fernet(key)
        
        # Cache the key for performance
        self._key_cache[context] = fernet
        return fernet
    
    def encrypt_field(self, value: str, context: str = "default") -> str:
        """
        Encrypt a field value.
        
        Args:
            value: The string value to encrypt
            context: Encryption context for key derivation
            
        Returns:
            Base64 encoded encrypted value
        """
        if not value:
            return value
        
        try:
            fernet = self._derive_key(context)
            encrypted_bytes = fernet.encrypt(value.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed for context {context}: {str(e)}")
            raise
    
    def decrypt_field(self, encrypted_value: str, context: str = "default") -> str:
        """
        Decrypt a field value.
        
        Args:
            encrypted_value: Base64 encoded encrypted value
            context: Encryption context used for encryption
            
        Returns:
            Decrypted string value
        """
        if not encrypted_value:
            return encrypted_value
        
        try:
            fernet = self._derive_key(context)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode('utf-8'))
            decrypted_bytes = fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed for context {context}: {str(e)}")
            raise
    
    def encrypt_dict(self, data: Dict[str, Any], fields_to_encrypt: list, context: str = "default") -> Dict[str, Any]:
        """
        Encrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary containing data to encrypt
            fields_to_encrypt: List of field names to encrypt
            context: Encryption context
            
        Returns:
            Dictionary with encrypted fields
        """
        encrypted_data = data.copy()
        
        for field in fields_to_encrypt:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt_field(str(encrypted_data[field]), context)
        
        return encrypted_data
    
    def decrypt_dict(self, encrypted_data: Dict[str, Any], fields_to_decrypt: list, context: str = "default") -> Dict[str, Any]:
        """
        Decrypt specific fields in a dictionary.
        
        Args:
            encrypted_data: Dictionary containing encrypted data
            fields_to_decrypt: List of field names to decrypt
            context: Encryption context used for encryption
            
        Returns:
            Dictionary with decrypted fields
        """
        decrypted_data = encrypted_data.copy()
        
        for field in fields_to_decrypt:
            if field in decrypted_data and decrypted_data[field]:
                decrypted_data[field] = self.decrypt_field(decrypted_data[field], context)
        
        return decrypted_data
    
    def create_secure_hash(self, value: str, salt: Optional[str] = None) -> str:
        """
        Create a secure hash of a value (for non-reversible hashing).
        Useful for client phone numbers, etc.
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 for secure hashing
        key = hashlib.pbkdf2_hmac('sha256', value.encode(), salt.encode(), 100000)
        return f"{salt}:{base64.urlsafe_b64encode(key).decode()}"
    
    def verify_secure_hash(self, value: str, hashed_value: str) -> bool:
        """Verify a value against its secure hash"""
        try:
            salt, hash_b64 = hashed_value.split(':', 1)
            expected_hash = base64.urlsafe_b64decode(hash_b64)
            actual_hash = hashlib.pbkdf2_hmac('sha256', value.encode(), salt.encode(), 100000)
            return hmac.compare_digest(expected_hash, actual_hash)
        except (ValueError, TypeError):
            return False


class DataProtectionService:
    """
    GDPR-compliant data protection service.
    Handles data anonymization, retention, and deletion.
    """
    
    def __init__(self, encryption_service: EncryptionService):
        self.encryption = encryption_service
        
        # Define which fields contain PII and need special handling
        self.pii_fields = {
            'client': ['client_name', 'client_phone', 'client_email', 'notes'],
            'user': ['email', 'full_name'],
            'booking': ['client_name', 'client_phone', 'client_email', 'notes']
        }
    
    def anonymize_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize user data while preserving analytics value.
        
        Args:
            user_data: Dictionary containing user data
            
        Returns:
            Anonymized user data
        """
        anonymized = user_data.copy()
        
        # Replace identifiable information with anonymized versions
        if 'email' in anonymized:
            # Keep domain for analytics, anonymize user part
            email = anonymized['email']
            if '@' in email:
                domain = email.split('@')[1]
                anonymized['email'] = f"anonymized_{secrets.token_hex(4)}@{domain}"
            else:
                anonymized['email'] = f"anonymized_{secrets.token_hex(8)}"
        
        if 'full_name' in anonymized:
            anonymized['full_name'] = "Anonymized User"
        
        if 'username' in anonymized:
            anonymized['username'] = f"anon_{secrets.token_hex(6)}"
        
        # Add anonymization timestamp
        anonymized['anonymized_at'] = datetime.utcnow().isoformat()
        
        return anonymized
    
    def encrypt_sensitive_fields(self, data: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
        """
        Encrypt sensitive fields based on entity type.
        
        Args:
            data: Data dictionary
            entity_type: Type of entity (client, user, booking)
            
        Returns:
            Data with encrypted sensitive fields
        """
        if entity_type not in self.pii_fields:
            return data
        
        fields_to_encrypt = self.pii_fields[entity_type]
        return self.encryption.encrypt_dict(data, fields_to_encrypt, entity_type)
    
    def decrypt_sensitive_fields(self, encrypted_data: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
        """
        Decrypt sensitive fields based on entity type.
        
        Args:
            encrypted_data: Data dictionary with encrypted fields
            entity_type: Type of entity (client, user, booking)
            
        Returns:
            Data with decrypted sensitive fields
        """
        if entity_type not in self.pii_fields:
            return encrypted_data
        
        fields_to_decrypt = self.pii_fields[entity_type]
        return self.encryption.decrypt_dict(encrypted_data, fields_to_decrypt, entity_type)
    
    def create_data_export(self, user_id: int, db_session) -> Dict[str, Any]:
        """
        Create GDPR-compliant data export for a user.
        
        Args:
            user_id: User ID to export data for
            db_session: Database session
            
        Returns:
            Complete data export
        """
        from app.models.user import User
        from app.models.booking import Booking
        
        export_data = {
            'export_date': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'data': {}
        }
        
        # Get user data
        user = db_session.query(User).filter(User.id == user_id).first()
        if user:
            user_data = {
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role.name,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login
            }
            export_data['data']['user'] = user_data
        
        # Get related bookings if user is client
        bookings = db_session.query(Booking).filter(
            Booking.client_email == user.email
        ).all()
        
        if bookings:
            booking_data = []
            for booking in bookings:
                booking_info = {
                    'id': booking.id,
                    'date': booking.date.isoformat() if booking.date else None,
                    'start_time': booking.start_time.isoformat() if booking.start_time else None,
                    'end_time': booking.end_time.isoformat() if booking.end_time else None,
                    'total_price': booking.total_price,
                    'status': booking.status,
                    'created_at': booking.created_at.isoformat() if booking.created_at else None
                }
                booking_data.append(booking_info)
            export_data['data']['bookings'] = booking_data
        
        return export_data
    
    def schedule_data_deletion(self, user_id: int, retention_days: int = 30) -> Dict[str, Any]:
        """
        Schedule data for deletion after retention period.
        
        Args:
            user_id: User ID to schedule for deletion
            retention_days: Days to retain data before deletion
            
        Returns:
            Deletion schedule information
        """
        from datetime import datetime, timedelta
        
        deletion_date = datetime.utcnow() + timedelta(days=retention_days)
        
        # In a production system, this would create a scheduled job
        # For now, we'll return the schedule information
        return {
            'user_id': user_id,
            'scheduled_deletion_date': deletion_date.isoformat(),
            'retention_days': retention_days,
            'status': 'scheduled'
        }


# Global instances for cost-effective singleton pattern
encryption_service = EncryptionService()
data_protection_service = DataProtectionService(encryption_service)


# Utility functions for easy access
def encrypt_client_data(client_data: Dict[str, Any]) -> Dict[str, Any]:
    """Encrypt sensitive client data"""
    return data_protection_service.encrypt_sensitive_fields(client_data, 'client')


def decrypt_client_data(encrypted_client_data: Dict[str, Any]) -> Dict[str, Any]:
    """Decrypt sensitive client data"""
    return data_protection_service.decrypt_sensitive_fields(encrypted_client_data, 'client')


def encrypt_booking_data(booking_data: Dict[str, Any]) -> Dict[str, Any]:
    """Encrypt sensitive booking data"""
    return data_protection_service.encrypt_sensitive_fields(booking_data, 'booking')


def decrypt_booking_data(encrypted_booking_data: Dict[str, Any]) -> Dict[str, Any]:
    """Decrypt sensitive booking data"""
    return data_protection_service.decrypt_sensitive_fields(encrypted_booking_data, 'booking')