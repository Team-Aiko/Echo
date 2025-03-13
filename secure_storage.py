import os
import base64
import json
import logging
import sys
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# 🔒 Secure Logging Setup (Prevents leaking sensitive data)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🔑 Secure File Paths
KEY_FILE = "encryption_key.key"
CONFIG_FILE = "secure_config.dat"
SALT_FILE = "salt.key"

# 🔄 Constants for Encryption
ITERATIONS = 100000  # PBKDF2 Iterations
BLOCK_SIZE = 16  # AES Block size

# ✅ Secure Masking for Debugging
def secure_mask(value, visible_digits=4):
    """Mask sensitive values before logging."""
    value = str(value)
    return "*" * (len(value) - visible_digits) + value[-visible_digits:]

# 🔑 Generate a Secure Random Salt
def generate_salt():
    """Generates and stores a secure salt for key derivation."""
    if not os.path.exists(SALT_FILE):
        salt = secrets.token_bytes(16)
        with open(SALT_FILE, "wb") as f:
            f.write(salt)
    else:
        with open(SALT_FILE, "rb") as f:
            salt = f.read()
    return salt

# 🔑 Generate Key from Password
def generate_key(password: bytes):
    """Derives a secure encryption key from a password."""
    salt = generate_salt()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend(),
    )
    return kdf.derive(password)

# 🔐 Generate a Secure Hidden Key
def generate_hidden_key():
    """Creates a secure key and hides the bot token inside it."""
    if os.path.exists(KEY_FILE):
        logging.warning("⚠️ Key file already exists! Regenerating will invalidate current credentials.")
    
    bot_token = input("Enter your Discord Bot Token: ").strip()
    if not bot_token:
        logging.critical("❌ Bot token cannot be empty!")
        return

    # Generate a secure key from the bot token
    key = generate_key(bot_token.encode())
    
    # Store the key securely
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(base64.urlsafe_b64encode(key))
    
    logging.info("🔑 Secure encryption key generated and stored.")
    
    return key

# 🔓 Load Encryption Key
def load_encryption_key():
    """Loads and validates the encryption key."""
    if not os.path.exists(KEY_FILE):
        logging.critical("❌ Encryption key not found! Run `secure_storage.py setup` first.")
        return None

    with open(KEY_FILE, "rb") as key_file:
        key = base64.urlsafe_b64decode(key_file.read())

    if len(key) != 32:
        logging.critical("❌ Invalid encryption key detected! Regenerate it.")
        return None

    logging.info("🔑 Encryption key successfully loaded.")
    return key

# 🔒 Encrypt Bot Credentials
def encrypt_data(credentials: dict):
    """Encrypts bot credentials and securely stores them."""
    key = load_encryption_key()
    if not key:
        return

    # Convert credentials to JSON
    data = json.dumps(credentials).encode()

    # Generate a random IV (Initialization Vector)
    iv = os.urandom(BLOCK_SIZE)

    # AES-256 Encryption
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Padding for AES (PKCS7 Padding)
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    padded_data = data + bytes([pad_len] * pad_len)

    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Store IV and encrypted data together
    with open(CONFIG_FILE, "wb") as config_file:
        config_file.write(iv + encrypted_data)

    logging.info("✅ Bot credentials encrypted and stored securely.")

# 🔓 Decrypt Bot Credentials
def decrypt_data():
    """Decrypts bot credentials securely."""
    key = load_encryption_key()
    if not key:
        return None

    if not os.path.exists(CONFIG_FILE):
        logging.critical("❌ Encrypted credentials file not found! Run `secure_storage.py encrypt` first.")
        return None

    with open(CONFIG_FILE, "rb") as config_file:
        encrypted_data = config_file.read()

    iv, encrypted_payload = encrypted_data[:BLOCK_SIZE], encrypted_data[BLOCK_SIZE:]

    # AES-256 Decryption
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_padded_data = decryptor.update(encrypted_payload) + decryptor.finalize()

    # Remove padding
    pad_len = decrypted_padded_data[-1]
    decrypted_data = decrypted_padded_data[:-pad_len]

    # Convert back to dictionary
    bot_config = json.loads(decrypted_data.decode())

    logging.info("🔓 Bot credentials successfully decrypted.")

    return bot_config

# 🔄 Command-Line Interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("⚠️ Please specify `setup`, `encrypt`, or `decrypt` as an argument.")
        exit(1)

    command = sys.argv[1].lower()

    if command == "setup":
        generate_hidden_key()

    elif command == "encrypt":
        credentials = {
            "DISCORD_BOT_TOKEN": input("Enter your Discord Bot Token: ").strip(),
            "DISCORD_GUILD_ID": input("Enter your Discord Guild ID: ").strip(),
            "DISCORD_CLIENT_ID": input("Enter your Discord Client ID: ").strip(),
        }

        if not all(credentials.values()):
            logging.critical("❌ All fields must be filled!")
            exit(1)

        encrypt_data(credentials)

    elif command == "decrypt":
        decrypted_data = decrypt_data()
        if decrypted_data:
            logging.info("🔓 Bot credentials successfully decrypted.")

    else:
        logging.error("⚠️ Invalid argument. Use `setup`, `encrypt`, or `decrypt`.")
