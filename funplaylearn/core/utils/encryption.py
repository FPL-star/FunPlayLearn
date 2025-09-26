import os
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from cryptography.fernet import Fernet


def _get_fernet():
    if settings.DEBUG:
        # For dev, just use a temporary key
        dev_key = Fernet.generate_key()
        return Fernet(dev_key)
    else:
        key = os.environ.get("ENCRYPTION_KEY")
        if not key:
            raise ImproperlyConfigured("ENCRYPTION_KEY not set in production")
        return Fernet(key)


def encrypt_field(value: str | None) -> bytes | None:
    if not value:
        return None
    if settings.DEBUG:
        return value.encode()
    fernet = _get_fernet()
    return fernet.encrypt(value.encode())


def decrypt_field(value: bytes | None) -> str | None:
    if not value:
        return None
    if settings.DEBUG:
        return value.decode()
    fernet = _get_fernet()
    return fernet.decrypt(value).decode()
