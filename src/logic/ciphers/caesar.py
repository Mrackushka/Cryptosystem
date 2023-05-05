from cloup import option
from cloup.constraints import (
    constraint,
    require_one,
    accept_none,
    require_all,
    If,
)

from .base_cipher import BaseCipher
from ...ui import add_cipher_options


class Caesar(BaseCipher):
    def __init__(self, text, shift, phrase):
        super().__init__(text)
        self.unicode_size = int(0x110000)
        if shift is not None:
            self.shift = shift
            self._validate_shift()
        if phrase is not None:
            self.phrase = phrase
            self._validate_phrase()

    def encrypt(self):
        self._create_letter_shifts()
        return "".join(
            chr(ord(letter) + self._letter_shifts[letter])
            for letter in self.text
        )

    def decrypt(self):
        self.shift *= -1
        return self.encrypt()

    def bruteforce(self):
        for self.shift in range(1, self.unicode_size):
            decrypted_text = self.decrypt()
            if self.phrase in decrypted_text:
                positive_shift = self.shift * -1
                negative_shift = -(self.unicode_size - positive_shift)
                return (
                    f"Text was successfully decrypted with shift "
                    f"{positive_shift} or {negative_shift}. Result is:\n"
                    f"{decrypted_text}"
                )
        return "There is no such phrase in any possible text decryption :c"

    def _validate_shift(self):
        if self.shift == 0:
            self._terminate(
                "Are you seriously trying to use shift 0 in Caesar chipher?"
            )

    def _validate_phrase(self):
        if len(self.phrase) == 0:
            self._terminate("Where did the phrase go?")
        elif len(self.phrase) > len(self.text):
            self._terminate(
                "Are you seriously trying to use a phrase from text "
                "longer than text itself?"
            )

    def _terminate(self, message):
        print(message)
        exit(0)

    def _create_letter_shifts(self):
        self._letter_shifts = {
            letter: self._validate_shift_for_letter(letter)
            for letter in self.text
        }

    def _validate_shift_for_letter(self, letter):
        shifted_letter_unicode = ord(letter) + self.shift
        if shifted_letter_unicode < 0:
            unicodes_in_shift = (
                abs(shifted_letter_unicode) // self.unicode_size
            ) + 1
            return self.shift + unicodes_in_shift * self.unicode_size
        elif shifted_letter_unicode >= self.unicode_size:
            unicodes_in_shift = shifted_letter_unicode // self.unicode_size
            return self.shift - unicodes_in_shift * self.unicode_size
        else:
            return self.shift


add_cipher_options(
    Caesar,
    option(
        "-s",
        "--shift",
        type=int,
        help="caesar cipher shift",
    ),
    constraint(require_one, ("bruteforce", "shift")),
    option(
        "-p",
        "--phrase",
        help="known decrypted phrase from encrypted text which allows to "
        "determine correct one from possible decryptions",
    ),
    constraint(
        If(
            "bruteforce",
            then=require_all,
            else_=accept_none.rephrased(
                error="--phrase should not be provided"
            ),
        ),
        ("phrase", "bruteforce"),
    ),
)
