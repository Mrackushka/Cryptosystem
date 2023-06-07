from cloup import option, Path, Choice
from cloup.constraints import constraint, require_one
from enum import Enum
from base64 import b64encode, b64decode
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad

from .base_cipher import BaseCipher
from ..file_operations import load_text_from_file
from ...ui import add_cipher_options


class des_modes(Enum):
    ecb = DES.MODE_ECB
    cbc = DES.MODE_CBC
    cfb = DES.MODE_CFB
    ofb = DES.MODE_OFB
    ctr = DES.MODE_CTR


class Des(BaseCipher):
    def __init__(self, text: str, key: str, key_from_file: str, mode: str):
        self.unicode_size = int(0x110000)
        if key_from_file is not None:
            key = load_text_from_file(key_from_file)
        self.key = self._validate_key(key)
        self.text = text
        self.mode = des_modes[mode]

    def encrypt(self) -> str:
        if self.mode == des_modes.ctr:
            cipher = DES.new(self.key.encode("utf-8"), self.mode.value, nonce=b"")
            encrypted_text = b64encode(
                cipher.encrypt(self.text.encode("utf-8"))
            ).decode("utf-8")
        else:
            cipher = DES.new(self.key.encode("utf-8"), self.mode.value)
            encrypted_text = b64encode(
                cipher.encrypt(pad(self.text.encode("utf-8"), DES.block_size))
            ).decode("utf-8")
        if self.mode in (des_modes.ecb, des_modes.ctr):
            return encrypted_text
        else:
            iv = b64encode(cipher.iv).decode("utf-8")  # type: ignore
            return encrypted_text + iv

    def decrypt(self) -> str:
        try:
            if self.mode == des_modes.ecb:
                cipher = DES.new(self.key.encode("utf-8"), self.mode.value)
            elif self.mode == des_modes.ctr:
                cipher = DES.new(self.key.encode("utf-8"), self.mode.value, nonce=b"")
                return cipher.decrypt(b64decode(self.text)).decode("utf-8")
            else:
                iv = self.text[-12:]
                self.text = self.text[:-12]
                cipher = DES.new(
                    self.key.encode("utf-8"), self.mode.value, b64decode(iv)
                )
            return unpad(cipher.decrypt(b64decode(self.text)), DES.block_size).decode(
                "utf-8"
            )
        except ValueError:
            self._terminate(
                f"This text was not encrypted using {self.mode.name.upper()} mode"
            )
            return ""

    def bruteforce(self) -> str:
        return "NotImplemented"

    def _validate_key(self, key: str) -> str:
        byte_key = key.encode("utf-8")
        key_len = len(byte_key)
        if key_len != 8:
            self._terminate(f"Key must be 8 bytes length (but {key_len} was given)")
        return key

    def _terminate(self, message):
        print(message)
        exit(0)


add_cipher_options(
    Des,
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
    option(
        "-m",
        "--mode",
        type=Choice(["ecb", "cbc", "cfb", "ofb", "ctr", "openpgp", "eax"]),
        required=True,
        help="""
            one of DES cipher modes:

            \b
            - ECB
            - CBC
            - CFB
            - OFB
            - CTR
            - OPENPGP
            - EAX
        """,
    ),
)
