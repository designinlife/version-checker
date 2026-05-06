import json
from compression import zstd
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click
from click.core import Context
from jinja2 import Template
from loguru import logger

from app.core.config import Configuration
from app.core.notify import send_mail
from app.core.output import get_output_dir


def _filter_nones(obj):
    """递归移除 JSON 结构中的 None 值，避免合并输出包含空字段。"""

    if isinstance(obj, list):
        filtered_values = (_filter_nones(j) for j in obj)
        return [i for i in filtered_values if i is not None]
    elif isinstance(obj, dict):
        filtered_items = ((i, _filter_nones(j)) for i, j in obj.items())
        return {k: v for k, v in filtered_items if v is not None}
    else:
        return obj


def _compare_json_data(new_data: List[Dict], old_data: Optional[List[Dict]] = None) -> List[Tuple[str, str, str]]:
    """对比新旧合并数据中的 latest 字段，返回需要通知的版本变化列表。"""

    if old_data is None:
        return []

    updates: List[Tuple[str, str, str]] = []
    old_data_dict: Dict[str, str] = {item["name"]: item["latest"] for item in old_data if "name" in item and "latest" in item}

    for new_item in new_data:
        if "name" in new_item and "latest" in new_item:
            name = new_item["name"]
            display_name = new_item["display_name"] if "display_name" in new_item and new_item["display_name"] != "" else new_item["name"]
            latest = new_item["latest"]
            previous = old_data_dict.get(name)

            if previous != latest:
                updates.append((display_name, latest, previous if previous is not None else ""))
    return updates


filter_nones = _filter_nones
compare_json_data = _compare_json_data


def combine_data(cfg: Configuration):
    """合并输出目录中的单软件 JSON 文件，并生成 `all.json` 与 `all.json.zst`。

    合并前会读取旧 `all.json` 作为对比基线；首次生成时没有旧数据，因此不会产生差异通知。
    """
    p = get_output_dir(cfg.workdir)
    all_json_file = p.joinpath("all.json")
    old_all_json = None

    if all_json_file.exists():
        with open(all_json_file, "r", encoding="utf-8") as f:
            old_all_json = json.loads(f.read())

    data = []

    for file in p.glob("*.json"):
        if file.name != "all.json":
            with open(file, "r", encoding="utf-8") as f:
                data.append(json.loads(f.read()))

    new_all_json = sorted(_filter_nones(data), key=lambda x: x["name"])

    with open(p.joinpath("all.json"), "w", encoding="utf-8") as f:
        b = json.dumps(new_all_json, ensure_ascii=True, separators=(",", ":"))
        f.write(b)

        with zstd.open(p.joinpath("all.json.zst"), "wb") as zstf:
            zstf.write(b.encode("utf-8"))

    # 差异仅用于通知和日志，不影响合并产物写入。
    differences = _compare_json_data(new_all_json, old_all_json)

    return new_all_json, differences


def send_update_notification(cfg: Configuration, email_data: List[Dict[str, str]]) -> bool:
    """按差异列表渲染邮件模板并发送通知，模板缺失或发送失败都不影响合并结果。"""
    template_file = Path(cfg.workdir).joinpath("email_notify.j2")
    if not template_file.is_file():
        logger.warning("Email notification skipped: template file does not exist.")
        return False

    with open(template_file, "r", encoding="utf-8") as f:
        template = Template(f.read())

    html_content = template.render(items=email_data)
    ok_email = send_mail(
        to=["codeplus@qq.com"], subject="Github Notification from version-checker", content="No Content", html=html_content
    )
    logger.info(f"Send email result: {ok_email}")
    return ok_email


@click.command("combine", help="Merge JSON data into a file.")
@click.option("--notify", "notify", help="Send email notification when differences are found.", is_flag=True)
@click.pass_obj
@click.pass_context
def cli(ctx: Context, cfg: Configuration, notify: bool):
    """执行输出合并命令；只有显式传入 --notify 时才发送邮件通知。"""
    logger.debug(f"app cli combine called. (Working directory: {cfg.workdir} | Title: {cfg.settings.app.title})")

    _, differences = combine_data(cfg)

    logger.info("The all.json file has been generated.")

    if differences:
        logger.info("The following differences were found:")

        email_data = []

        for name, latest, previous in differences:
            email_data.append({"name": name, "latest": latest, "previous": previous})

            logger.info(f"{name}: {previous} -> {latest}")

        if notify:
            send_update_notification(cfg, email_data)
    else:
        logger.info("No differences were found.")
