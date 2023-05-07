from cryptography.fernet import Fernet

# Generate a new key and store it in a file for reuse
key = Fernet.generate_key()
with open('fernet.key', 'wb') as f:
    f.write(key)

# Load the key from the file
with open('fernet.key', 'rb') as f:
    key = f.read()

# Create a Fernet instance with the loaded key
fernet = Fernet(key)
