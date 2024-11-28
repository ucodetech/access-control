# Generate a key (do this once and store it securely, e.g., in your settings)
from cryptography.fernet import Fernet

key = Fernet.generate_key()
print(key)  # Save this key and use it in your project
