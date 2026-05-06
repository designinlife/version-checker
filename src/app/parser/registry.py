import importlib
from typing import Iterable, Type

from app.core.config import AppSettingSoftItem
from app.parser import Base


def parser_to_module_name(parser_name: str) -> str:
    """把配置中的 parser 名称转换为对应的 Python 模块名。"""
    return parser_name.replace("-", "_")


def load_parser_class(parser_name: str) -> Type[Base]:
    """加载 parser 对应的 `Parser` 类，并校验它继承自解析器基类。"""
    module_name = parser_to_module_name(parser_name)
    module = importlib.import_module(f"app.parser.{module_name}")
    parser_class = getattr(module, "Parser")

    if not issubclass(parser_class, Base):
        raise TypeError(f"Parser '{parser_name}' must inherit from app.parser.Base.")

    return parser_class


def validate_parser_contracts(softwares: Iterable[AppSettingSoftItem]) -> list[str]:
    """批量校验配置中使用到的 parser 是否能加载并满足基类契约。"""
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
