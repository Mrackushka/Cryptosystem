from .base_cipher import BaseCipher

from importlib import import_module
from pathlib import Path
from pkgutil import iter_modules


def import_ciphers():
    modules_path = Path(__file__).parent.resolve()
    module_names = [
        f".{name}" for _, name, _ in iter_modules([str(modules_path)])
    ]
    for module_name in module_names:
        module = import_module(module_name, __name__)
        ciphers = [c.__name__ for c in BaseCipher.__subclasses__()]
        module_classes = [c for c in dir(module) if c in ciphers]
        for cls in module_classes:
            globals()[cls] = getattr(module, cls)
