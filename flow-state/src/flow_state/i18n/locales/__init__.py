"""Language packs. One file per language.

To add a language, copy `fr.py` to `<code>.py`, change CODE / NAME / RTL /
QT_LOCALE / ORDER and translate the values. It is discovered automatically.
Run `pytest tests/test_i18n.py` to list any missing keys.
"""
import importlib
import pkgutil


def load_packs():
    packs = {}
    for info in pkgutil.iter_modules(__path__):
        if info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{__name__}.{info.name}")
        packs[module.CODE] = module
    return dict(sorted(packs.items(), key=lambda kv: getattr(kv[1], "ORDER", 999)))
