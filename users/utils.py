from cryptography.fernet import Fernet
from random import choice


def generate_code() -> str:
    password: str = ''
    numbers: tuple = ('1234567890')

    for _ in range(4):
        password += choice(choice(numbers))
    print(f"One Time Password(OTP): {password}")
    return password

def cryptography_fernet_encoder(password: str) -> str:
    key = Fernet.generate_key()
    fernet = Fernet(key)

    encMessage = fernet.encrypt(password.encode())

    return encMessage, key

def cryptography_fernet_decoder(password: str, key: str) -> str:
    fernet = Fernet(key)
    password = fernet.decrypt(password).decode()

    return password
