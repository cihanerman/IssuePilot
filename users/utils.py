from cryptography.fernet import Fernet

from IssuePilot import settings

cipher_suite = Fernet(settings.FERNET_KEY.encode())


def encrypt_data(data: str) -> str:
    """
    Encrypts the given data using a cipher suite.

    Args:
        data (str): The data to be encrypted.

    Returns:
        bytes: The encrypted data.

    """
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data.decode()


def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypts the given encrypted data and returns the decrypted string.

    Args:
        encrypted_data (bytes): The encrypted data to be decrypted.

    Returns:
        str: The decrypted string.

    """
    decrypted_data = cipher_suite.decrypt(encrypted_data).decode()
    return decrypted_data
