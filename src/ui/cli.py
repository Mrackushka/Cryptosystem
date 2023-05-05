from cloup import group, option_group, option, Path
from cloup.constraints import require_one, constraint

from functools import reduce

from ..logic import BaseCipher, import_ciphers, OptionsParser


common_cipher_option_names = ["encrypt", "decrypt", "bruteforce"]
common_cipher_options = [
    option_group(
        "Cipher method options",
        option(
            "-e",
            "--encrypt",
            is_flag=True,
            help="encrypt given text",
        ),
        option(
            "-d",
            "--decrypt",
            is_flag=True,
            help="decrypt given text",
        ),
        option(
            "-b",
            "--bruteforce",
            is_flag=True,
            help="bruteforce given encrypted text",
        ),
        constraint=require_one,
    ),
    option("-t", "--text", type=str, help="read input data from text"),
    option("-f", "--file", type=Path(), help="read input data from file"),
    option("-o", "--out", type=Path(), help="write output to file"),
    constraint(require_one, ("text", "file")),
]


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
        cipher_func = cipher_func_factory(cipher)
        globals()[cipher_name] = cipher_func
        decorators = (
            cryptosystem_cli.command(cipher_name),
            *common_cipher_options,
            *cipher_sppecific_options.get(cipher_name, [lambda func: func]),
        )
        apply_decorators(cipher_func, decorators)
    cryptosystem_cli()


def cipher_func_factory(cipher):
    def cipher_func(**cli_options):
        (
            cli_options,
            input_text,
            cipher_method_name,
            file_writer,
        ) = OptionsParser(
            cli_options, common_cipher_option_names
        ).parse_options()
        cipher_method = getattr(
            cipher(input_text, **cli_options),
            cipher_method_name,
        )
        cipher_result = cipher_method()
        file_writer(cipher_result)
    return cipher_func
