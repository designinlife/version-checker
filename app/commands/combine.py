import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import click
from click.core import Context
from loguru import logger

from app.core.config import Configuration


def compare_json_data(new_data: List[Dict], old_data: Optional[List[Dict]] = None) -> List[Tuple[str, str, str]]:
    """
    Compares the 'latest' version of data in two JSON-like lists of dictionaries.

    Args:
        new_data: A list of dictionaries representing the new data.
        old_data: An optional list of dictionaries representing the old data.  If None, it's treated as no previous data.

    Returns:
        A list of tuples. Each tuple contains (name, latest, previous) where:
            - name: The 'name' key from the new_data dictionary.
            - latest: The 'latest' value from the new_data dictionary.
            - previous: The 'latest' value from the old_data dictionary, or None if not found.

        The list only contains tuples where the 'latest' version in new_data is different from the 'latest' version in old_data,
        or when the 'name' key is not found in old_data.  Returns an empty list if old_data is None.
    """

    if old_data is None:
        return []

    updates: List[Tuple[str, str, str]] = []
    old_data_dict: Dict[str, str] = {item['name']: item['latest'] for item in old_data if 'name' in item and 'latest' in item}

    for new_item in new_data:
        if 'name' in new_item and 'latest' in new_item:
            name = new_item['name']
            latest = new_item['latest']
            previous = old_data_dict.get(name)

            if previous != latest:
                updates.append((name, latest, previous if previous is not None else ""))
    return updates


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
        for name, latest, previous in differences:
            logger.info(f'{name}: {previous} -> {latest}')
    else:
        logger.info('No differences were found.')
