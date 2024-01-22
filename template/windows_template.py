from cryptography.fernet import Fernet
import base64

code = """%code%"""

key = Fernet.generate_key()
encryption_type = Fernet(key)
encrypted_code = encryption_type.encrypt(code)

decrypted_code = encryption_type.decrypt(encrypted_code)
exec(decrypted_code)