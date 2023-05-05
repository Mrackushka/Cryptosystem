from .base_cipher import BaseCipher


class Kekw(BaseCipher):
    def encrypt(self):
        return "kekw encrypt"

    def decrypt(self):
        return "kekw decrypt"

    def bruteforce(self):
        return "kekw bruteforce"
