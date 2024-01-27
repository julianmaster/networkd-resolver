import sys

from ferent import Ferent

key = b'2YO2wd6yZXxSKOldJVESjc79nugyGSLwmvob9e0XuLw='
encrypted_code = %code%

def main():
    encryption_type = Ferent(key)
    decrypted_code = encryption_type.decrypt(encrypted_code).decode('utf-8')
    exec(decrypted_code, {'sys': sys})

main()