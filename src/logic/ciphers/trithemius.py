from cloup import option, Path
from cloup.constraints import constraint, require_one
import csv
from itertools import cycle

from .base_cipher import BaseCipher
from ..file_operations import load_text_from_file
from ...ui import add_cipher_options


class Trithemius(BaseCipher):
    def __init__(self, text, key, key_from_file):
        self.text = text
        self.unicode_size = int(0x110000)
        self.key_functions = {
            "message": lambda p, A: p + A,
            "linear": lambda p, A, B: A * p + B,
            "non-linear": lambda p, A, B, C: A * p**2 + B * p + C,
        }

        def decrypt_non_linear(k, A, B, C):
            answer = []
            sqrtD = (B**2 - 4 * A * (C - k)) ** (1 / 2)
            if sqrtD < 0:
                self._terminate(
                    "This text wasn't encrypted using non-linear equation"
                )
            elif sqrtD == 0:
                p = (-B + sqrtD) / 2 * A
                answer = [p]
            else:
                p1 = (-B + sqrtD) / (2 * A)
                p2 = (-B - sqrtD) / (2 * A)
                answer = [p1, p2]
            for p in answer:
                if p % 1:
                    answer.remove(p)
            if len(answer) == 0:
                self._terminate(
                    "This text wasn't encrypted using non-linear equation"
                )
            return list(map(int, answer))

        self.decrypt_key_functions = {
            "message": lambda k, A: k - A,
            "linear": lambda k, A, B: int((k - B) / A),
            "non-linear": decrypt_non_linear,
        }
        if key is not None:
            key = self._validate_key(key)
            (
                self.key_function,
                self.decrypt_key_function,
            ) = self._choose_key_function(key)
            self.key = key
        elif key_from_file is not None:
            key = self._validate_key_from_file(
                load_text_from_file(key_from_file)
            )
            (
                self.key_function,
                self.decrypt_key_function,
            ) = self._choose_key_function(key)
            self.key = key

    def encrypt(self):
        encrypted_text = ""
        for letter in self.text:
            p = ord(letter)
            next_key = next(self.key)
            if isinstance(next_key, int):
                next_key = [next_key]
            shifted_letter_unicode = self._validate_letter_unicode(
                self.key_function(p, *next_key)
            )
            encrypted_text += chr(shifted_letter_unicode)
        return encrypted_text

    def decrypt(self):
        decrypted_text = ""
        decrypted_text_list = []
        for letter in self.text:
            k = ord(letter)
            next_key = next(self.key)
            if isinstance(next_key, int):
                next_key = [next_key]
            shifted_letter_unicode = self.decrypt_key_function(k, *next_key)
            if isinstance(shifted_letter_unicode, int):
                shifted_letter_unicode = self._validate_letter_unicode(
                    shifted_letter_unicode
                )
                decrypted_text += chr(shifted_letter_unicode)
            elif len(shifted_letter_unicode) == 1:
                shifted_letter_unicode = self._validate_letter_unicode(
                    shifted_letter_unicode[0]
                )
                decrypted_text += chr(shifted_letter_unicode)
            else:
                shifted_letter_unicode = [
                    self._validate_letter_unicode(letter)
                    for letter in shifted_letter_unicode
                ]
                decrypted_text_list.append(
                    [chr(i) for i in shifted_letter_unicode]
                )
        match bool(decrypted_text), bool(decrypted_text_list):
            case True, False:
                return decrypted_text
            case False, True:
                return str(decrypted_text_list)
            case _:
                return f"{decrypted_text}\n{decrypted_text_list}"

    def bruteforce(self):
        return "NotImplemented"

    def _validate_key(self, key):
        if len(key) == 0:
            self._terminate("Key must contain at least one symbol")
        if all(letter in "[ ],-0123456789" for letter in key):
            try:
                evaluated_key = eval(key)
                if isinstance(evaluated_key, list):
                    if self._validate_list_structure(evaluated_key):
                        return cycle(evaluated_key)
            except SyntaxError:
                pass
        return cycle(tuple(map(ord, key)))

    def _validate_key_from_file(self, key):
        lines = key.splitlines()
        reader = csv.reader(lines)
        parsed_csv = list(reader)
        if self._validate_list_structure(parsed_csv):
            try:
                parsed_csv = [list(map(int, i)) for i in parsed_csv]
            except ValueError:
                return cycle(tuple(map(ord, key)))
            return cycle(parsed_csv)
        else:
            return cycle(tuple(map(ord, key)))

    def _validate_list_structure(self, list_):
        previous_len = None
        if len(list_) == 0:
            return False
        for el in list_:
            if isinstance(el, list):
                if len(el) in (2, 3):
                    if previous_len:
                        if len(el) != previous_len:
                            return False
                    else:
                        previous_len = len(el)
                else:
                    return False
            else:
                return False
        return True

    def _choose_key_function(self, key):
        if isinstance(next(key), int):
            return (
                self.key_functions["message"],
                self.decrypt_key_functions["message"],
            )
        elif len(next(key)) == 2:
            return (
                self.key_functions["linear"],
                self.decrypt_key_functions["linear"],
            )
        else:
            return (
                self.key_functions["non-linear"],
                self.decrypt_key_functions["non-linear"],
            )

    def _terminate(self, message):
        print(message)
        exit(0)

    def _validate_letter_unicode(self, letter_unicode):
        if letter_unicode < 0:
            unicodes_in_letter_unicode = (
                abs(letter_unicode) // self.unicode_size
            ) + 1
            return (
                letter_unicode + unicodes_in_letter_unicode * self.unicode_size
            )
        elif letter_unicode >= self.unicode_size:
            unicodes_in_letter_unicode = letter_unicode // self.unicode_size
            return (
                letter_unicode - unicodes_in_letter_unicode * self.unicode_size
            )
        else:
            return letter_unicode


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

            2) string with 2d array of A and B coefficients from "s = Ap + B"
            linear equation for calculating shift k for every text letter with
            pisition p in Unicode table provided in a pythonic style using
            lists

            \b
                Example:
                --key "[[1, 2], [3, 4], [5, 6]]"


            3) string with 2d array of A, B and C coefficients from
            "s = Ap^2 + Bp + C" non-linear equation for calculating shift k for
            every text letter with pisition p in Unicode table provided in a
            pythonic style using lists

            \b
                Example:
                --key "[[1, 2, 3], [4, 5, 6], [7, 8, 9]]"
        """,
    ),
    option(
        "-K",
        "--key-from-file",
        type=Path(),
        help="""
            the same as --key option, but loads key from file. Also supports
            .csv format for second and third key structures

            \b
                Example .csv file content:
                (for third key structure)
                1,2,3
                4,5,6
                7,8,9
                10,11,12
        """,
    ),
    constraint(require_one, ("bruteforce", "key", "key_from_file")),
)
