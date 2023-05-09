from abc import ABC, abstractmethod


class BaseCipher(ABC):
    @abstractmethod
    def encrypt(self):
        ...

    @abstractmethod
    def decrypt(self):
        ...

    @abstractmethod
    def bruteforce(self):
        ...
