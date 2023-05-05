from abc import ABC, abstractmethod


class BaseCipher(ABC):
    def __init__(self, text):
        self.text = text

    @abstractmethod
    def encrypt(self):
        ...

    @abstractmethod
    def decrypt(self):
        ...

    @abstractmethod
    def bruteforce(self):
        ...
