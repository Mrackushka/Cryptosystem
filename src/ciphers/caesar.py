from cloup import option
from cloup.constraints import constraint, mutually_exclusive

from .base_cipher import BaseCipher
from ..ui import add_cipher_options


class Caesar(BaseCipher):
    def encrypt(self):
        pass

    def decrypt(self):
        pass

    def bruteforce(self):
        pass


add_cipher_options(
    Caesar,
    option(
        "-s",
        "--shift",
        type=int,
        required=True,
        help="caesar cipher shift",
    ),
    constraint(mutually_exclusive, ("bruteforce", "shift")),
)
