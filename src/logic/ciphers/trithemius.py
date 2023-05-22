from cloup import option, Path
from cloup.constraints import constraint, require_one
from itertools import cycle
from typing import Any, Sequence
from enum import Enum, auto

from .base_cipher import BaseCipher
from ..file_operations import load_text_from_file
from ...ui import add_cipher_options


class key_type(Enum):
    motto = auto()
    linear = auto()
    non_linear = auto()


class Trithemius(BaseCipher):
    def __init__(self, text: str, key: str, key_from_file: str):
        self._change_key_sign = False
        self.unicode_size = int(0x110000)
        self.text = text
        if key_from_file is not None:
            key = load_text_from_file(key_from_file)
        self.key = self._validate_key(key)
        self.key_type = self._get_key_type(key)
        self.cipher_func = self._get_cipher_func(self.key_type)

    def encrypt(self) -> str:
        key = self._cycle_key(self.key, self.key_type)
        return "".join(
            chr(self._validate_letter_unicode(ord(letter) + self.cipher_func(i, key)))
            for i, (letter, key) in enumerate(zip(self.text, key))
        )

    def decrypt(self) -> str:
        self._change_key_sign = True
        return self.encrypt()

    def bruteforce(self) -> str:
        return "NotImplemented"

    def motto_shift_func(self, _, key: int) -> int:
        return key

    def linear_shift_func(self, p: int, key: list[int]) -> int:
        A, B = key
        return A * p + B

    def non_linear_shift_func(self, p: int, key: list[int]) -> int:
        A, B, C = key
        return A * p**2 + B * p + C

    def _validate_key(self, key: str) -> str:
        if len(key) == 0:
            self._terminate("Key must contain at least one symbol")
        return key

    def _validate_letter_unicode(self, letter_unicode: int) -> int:
        return letter_unicode % self.unicode_size

    def _get_key_type(self, key: str) -> key_type:
        if evaluated_key := self._eval_key(key):
            if self._validate_key_structure(evaluated_key, 3):
                return key_type.non_linear
            elif self._validate_key_structure(evaluated_key, 2):
                return key_type.linear
        return key_type.motto

    def _cycle_key(self, key: str, key_type_: key_type):  # TYPE ???
        if key_type_ is key_type.motto:
            return cycle(
                [
                    ord(letter) if not self._change_key_sign else -ord(letter)
                    for letter in key
                ]
            )
        else:
            return cycle(
                [[num if not self._change_key_sign else -num for num in eval(key)]]
            )

    def _get_cipher_func(self, key_type_: key_type):  # TYPE ???
        functions = {
            key_type.non_linear: self.non_linear_shift_func,
            key_type.linear: self.linear_shift_func,
            key_type.motto: self.motto_shift_func,
        }
        return functions[key_type_]

    def _eval_key(self, key: str) -> Any | bool:
        if all(letter in "[( )],-0123456789" for letter in key):
            try:
                return eval(key)
            except SyntaxError:
                pass
        return False

    def _validate_key_structure(self, key: Any, length: int) -> bool:
        if isinstance(key, Sequence) and len(key) == length:
            if all(isinstance(el, int) for el in key):
                return True
        return False

    def _terminate(self, message):
        print(message)
        exit(0)


add_cipher_options(
    Trithemius,
    option(
        "-k",
        "--key",
        type=str,
        help="""
            trithemius cipher key, which is a string with one of the following
            structures:

            1) just any string which represents 1d array of shifts

            \b
                Example:
                --key "This is a key for Trithemius cipher"

            2) string with array of A and B coefficients from "s = Ap + B"
            linear equation for calculating shift k for every text letter with
            pisition p in Unicode table provided in a pythonic style using
            lists or tuples

            \b
                Examples:
                --key "[1, 2]"
                --key "(1, 2)"
                --key "1, 2"


            3) string with array of A, B and C coefficients from
            "s = Ap^2 + Bp + C" non-linear equation for calculating shift k for
            every text letter with pisition p in Unicode table provided in a
            pythonic style using lists or tuples

            \b
                Examples:
                --key "[1, 2, 3]"
                --key "(1, 2, 3)"
                --key "1, 2, 3"
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
