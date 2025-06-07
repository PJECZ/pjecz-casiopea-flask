"""
Cryptography API Key generator and decoder
"""

import base64

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..config.settings import get_settings

settings = get_settings()


def convert_string_to_fernet_key(input_string: str) -> bytes:
    """Converts a string to a Fernet compatible encryption key"""
    input_string_bytes = input_string.encode("utf-8")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # Fernet requires 32 raw bytes for its key material
        salt=settings.SALT.encode("utf-8"),  # Salt for the Key Derivation Function
        iterations=600000,  # OWASP recommendation (as of early 2024)
        backend=default_backend(),
    )
    derived_key_bytes = kdf.derive(input_string_bytes)
    return base64.urlsafe_b64encode(derived_key_bytes)


def generate_api_key(email: str) -> str:
    """Generarte API Key"""
    fernet = Fernet(settings.FERNET_KEY)
    email_bytes = email.encode("utf-8")
    encrypted_email_bytes = fernet.encrypt(email_bytes)
    return encrypted_email_bytes.decode("utf-8")


def decode_api_key(api_key: str) -> str:
    """Decode API Key"""
    fernet = Fernet(settings.FERNET_KEY)
    api_key_bytes = api_key.encode("utf-8")
    try:
        decrypted_email_bytes = fernet.decrypt(api_key_bytes)
        return decrypted_email_bytes.decode("utf-8")
    except InvalidToken:
        return ""
