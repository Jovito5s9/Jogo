import os
import sys
from typing import Union, Sequence

def resource_path(relative_path: Union[str, Sequence[str]]) -> str:
    base_path = sys._MEIPASS if hasattr(sys, "_MEIPASS") else os.path.abspath(".")

    if isinstance(relative_path, (list, tuple)):
        parts = [str(p) for p in relative_path if str(p) not in ("", ".")]
    else:
        normalized = str(relative_path).replace("\\", "/")
        parts = [p for p in normalized.split("/") if p not in ("", ".")]

    return os.path.join(base_path, *parts)