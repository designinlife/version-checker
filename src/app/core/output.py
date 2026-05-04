import os
from pathlib import Path


def get_output_dir(workdir: str | Path | None) -> Path:
    """返回运行数据输出目录。"""
    base = Path(workdir or ".")
    output_subdir = os.environ.get("OUTPUT_DATA_DIR", "data")
    output_path = Path(output_subdir)
    if output_path.is_absolute():
        return output_path
    return base.joinpath(output_path)
