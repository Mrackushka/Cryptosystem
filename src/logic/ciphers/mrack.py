from .base_cipher import BaseCipher


class Mrack(BaseCipher):
    def encrypt(self):
        return "mrack encrypt"

    def decrypt(self):
        return "mrack decrypt"

    def bruteforce(self):
        return "mrack bruteforce"
