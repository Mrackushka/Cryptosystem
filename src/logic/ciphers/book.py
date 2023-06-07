from cloup import option, Path
from cloup.constraints import constraint, require_one
from random import choice

from .base_cipher import BaseCipher
from ..file_operations import load_text_from_file
from ...ui import add_cipher_options


class Book(BaseCipher):
    def __init__(self, text: str, key: str, key_from_file: str):
        self.unicode_size = int(0x110000)
        self.text = text
        if key_from_file is not None:
            key = load_text_from_file(key_from_file)
        key = self._validate_key(key)
        self.key = self._parse_key(key)

    def encrypt(self) -> str | None:
        encrypted_text = ""
        invalid_symbols = []
        for symbol in self.text:
            if positions := self.key.get(symbol):
                encrypted_text += f"{'/'.join(str(i) for i in choice(positions))}, "
            else:
                invalid_symbols.append(symbol)
        if invalid_symbols:
            self._terminate(
                f"Cannot operate symbols which are not in key: "
                f"{', '.join(invalid_symbols).strip()}"
            )
        else:
            return encrypted_text

    def decrypt(self) -> str:
        decrypted_text = ""
        for symbol in self.text.split(", "):
            try:
                symbol_tuple = tuple(int(i) for i in symbol.split("/"))
                for letter, positions in self.key.items():
                    if symbol_tuple in positions:
                        decrypted_text += letter
            except ValueError:
                decrypted_text += symbol
        return decrypted_text.strip()

    def bruteforce(self) -> str:
        return "NotImplemented"

    def _validate_key(self, key: str) -> str:
        if len(key) == 0:
            self._terminate("Key must contain at least one symbol")
        return key

    def _parse_key(self, key: str) -> dict[str, tuple[tuple[int, int]]]:
        key_list = key.strip().split("\n")
        key_dict = {symbol: [] for row in key_list for symbol in f"{row}\n"}
        for row_num, row in enumerate(key_list):
            for column_num, symbol in enumerate(f"{row}\n"):
                key_dict[symbol].append((row_num, column_num))
        return {k: tuple(v) for k, v in key_dict.items()}

    def _terminate(self, message):
        print(message)
        exit(0)


add_cipher_options(
    Book,
    option(
        "-k",
        "--key",
        type=str,
        help="""
            any poem, which contains maximum number of characters from the text to be
            encrypted
        """,
    ),
    option(
        "-K",
        "--key-from-file",
        type=Path(),
        help="""
            the same as --key option, but loads key from file.
        """,
    ),
    constraint(require_one, ("bruteforce", "key", "key_from_file")),
)
