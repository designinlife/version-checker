import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import click
from click.core import Context
from loguru import logger

from app.core.config import Configuration


def compare_json_data(new_data: List[Dict], old_data: Optional[List[Dict]] = None) -> List[Tuple[str, str]]:
    """
    比较两个JSON文件中的数据 latest 版本是否有更新。name 键名可能在其中一个文件中并不存在，应视为有新版本。

    Args:
        new_data: 新的JSON数据列表。
        old_data: 旧的JSON数据列表，默认为None。

    Returns:
        返回的数组中是一个元组对象，包含两个元素: name 和 latest，latest 是 new_data 中的值。
    """
    updated_list: List[Tuple[str, str]] = []

    if old_data is None:
        for item in new_data:
            if "name" in item and "latest" in item:
                updated_list.append((item["name"], item["latest"]))
            else:
                # 如果缺少 name 或 latest 键，跳过该条目或根据需求进行处理
                pass  # 或 raise ValueError("JSON data is missing 'name' or 'latest' key.")
        return updated_list

    old_data_dict: Dict[str, str] = {item.get("name"): item.get("latest") for item in old_data if "name" in item and "latest" in item}

    for new_item in new_data:
        if "name" not in new_item or "latest" not in new_item:
            continue  # skip entries without name and latest keys
        name = new_item["name"]
        latest = new_item["latest"]

        if name not in old_data_dict:
            updated_list.append((name, latest))
        elif old_data_dict[name] != latest:
            updated_list.append((name, latest))

    return updated_list


@click.command('combine', help='Merge JSON data into a file.')
@click.pass_obj
@click.pass_context
def cli(ctx: Context, cfg: Configuration):
    logger.debug(f'app cli combine called. (Working directory: {cfg.workdir} | Title: {cfg.settings.app.title})')

    # Merge the output JSON data files into all.json.
    p = Path(cfg.workdir).joinpath('data')

    all_json_file = p.joinpath('all.json')

    old_all_json = None

    if all_json_file.exists():
        with open(all_json_file, 'r', encoding='utf-8') as f:
            old_all_json = json.loads(f.read())

    data = []

    for file in p.glob('*.json'):
        if file.name != 'all.json':
            with open(file, 'r', encoding='utf-8') as f:
                data.append(json.loads(f.read()))

    new_all_json = sorted(data, key=lambda x: x['name'])

    with open(p.joinpath('all.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(new_all_json, ensure_ascii=True, separators=(',', ':')))

    logger.info('The all.json file has been generated.')

    # Compare the new and old data and print the differences.
    differences = compare_json_data(new_all_json, old_all_json)

    if differences:
        logger.info('The following differences were found:')
        for name, latest in differences:
            logger.info(f'{name}: {latest}')
    else:
        logger.info('No differences were found.')
