import importlib
from typing import Iterable, Type

from app.core.config import AppSettingSoftItem
from app.parser import Base


def parser_to_module_name(parser_name: str) -> str:
    return parser_name.replace("-", "_")


def load_parser_class(parser_name: str) -> Type[Base]:
    module_name = parser_to_module_name(parser_name)
    module = importlib.import_module(f"app.parser.{module_name}")
    parser_class = getattr(module, "Parser")

    if not issubclass(parser_class, Base):
        raise TypeError(f"Parser '{parser_name}' must inherit from app.parser.Base.")

    return parser_class


def validate_parser_contracts(softwares: Iterable[AppSettingSoftItem]) -> list[str]:
    errors: list[str] = []
    checked: set[str] = set()

    for soft in softwares:
        parser_name = soft.parser
        if parser_name in checked:
            continue
        checked.add(parser_name)

        try:
            load_parser_class(parser_name)
        except Exception as e:
            errors.append(f"{parser_name}: {type(e).__name__}: {e}")

    return sorted(errors)
