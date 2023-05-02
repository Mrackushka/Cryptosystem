from abc import ABC, abstractmethod


class BaseCipher(ABC):
    def __init__(self, **kwargs):
        print(kwargs)

    @abstractmethod
    def encrypt(self):
        ...

    @abstractmethod
    def decrypt(self):
        ...

    @abstractmethod
    def bruteforce(self):
        ...
