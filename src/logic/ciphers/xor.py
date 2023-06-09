from cloup import option, Path
from cloup.constraints import constraint, AcceptAtMost, require_one
import random

from .base_cipher import BaseCipher
from ..file_operations import load_text_from_file
from ...ui import add_cipher_options


class XOR(BaseCipher):
    def __init__(self, text: str, key: str, key_from_file: str, seed: int):
        self.text = text.strip()
        self.unicode_size = int(0x110000)
        self.message = ""
        if key is not None:
            self.key = self._validate_key(key)
        elif key_from_file is not None:
            self.key = self._validate_key(load_text_from_file(key_from_file))
        else:
            if seed is not None:
                random.seed(seed)
            self.key = self._generate_seed()
            # self.message = (
            # f"\n\nText was encrypted using this generated key:\n{self.key}"
            # )

    def encrypt(self) -> str:
        return "".join(
            [chr(ord(ch) ^ ord(k)) for ch, k in zip(self.text, self.key)]
        )

    def decrypt(self) -> str:
        return self.encrypt()

    def bruteforce(self) -> str:
        return "NotImplemented"

    def _validate_key(self, key: str) -> str:
        if not len(key):
            self._terminate("Key must contain at least one symbol")
        keys_in_text = len(self.text) // len(key) + 1
        full_key = key * keys_in_text
        return full_key.strip()

    def _generate_seed(self) -> str:
        return "".join(
            [
                chr(random.randint(0, self.unicode_size - 1))
                for _ in range(len(self.text))
            ]
        )

    def _terminate(self, message):
        print(message)
        exit(0)


add_cipher_options(
    XOR,
    option(
        "-k", "--key", type=str, help="xor cipher key, which is any string"
    ),
    option(
        "-K",
        "--key-from-file",
        type=Path(),
        help="the same as --key option, but loads key from file",
    ),
    constraint(AcceptAtMost(1), ("bruteforce", "key", "key_from_file")),
    option("-s", "--seed", type=int, help="Generate key by seed"),
    constraint(require_one, ("key", "key_from_file", "seed")),
)
