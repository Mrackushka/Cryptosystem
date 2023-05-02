from cloup import group, option_group, option
from cloup.constraints import require_one
from functools import reduce

from ..logic import BaseCipher, import_ciphers


common_cipher_options = option_group(
    "Cipher method options",
    option("-e", "--encrypt", is_flag=True, help="encrypt given text"),
    option("-d", "--decrypt", is_flag=True, help="decrypt given text"),
    option(
        "-b",
        "--bruteforce",
        is_flag=True,
        help="bruteforce given encrypted text",
    ),
    constraint=require_one,
)


cipher_sppecific_options = dict()


@group()
def cryptosystem_cli():
    pass


def apply_decorators(func, decorators):
    return reduce(
        lambda lower_decor, upper_decor: upper_decor(lower_decor),
        [func, *decorators[::-1]],
    )


def add_cipher_options(cipher_class, *options):
    cipher_sppecific_options[cipher_class.__name__.lower()] = options


def run_cryptosystem_cli():
    import_ciphers()
    for cipher in BaseCipher.__subclasses__():
        cipher_name = cipher.__name__.lower()

        def func(**kwargs):
            cipher(**kwargs)  # type: ignore

        globals()[cipher_name] = func
        decorators = (
            cryptosystem_cli.command(cipher_name),
            common_cipher_options,
            *cipher_sppecific_options.get(cipher_name, [lambda func: func]),
        )
        apply_decorators(func, decorators)
    cryptosystem_cli()
