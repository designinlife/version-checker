import json
from compression import zstd
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import click
from click.core import Context
from jinja2 import Template
from loguru import logger

from app.core.config import Configuration
from app.core.notify import send_mail


def filter_nones(obj):
    """
    Given a JSON-serializable object, return a copy without elements which have
    a value of None.
    """

    if isinstance(obj, list):
        # This version may or may not be easier to read depending on your
        # preferences:
        # return list(filter(None, map(remove_nones, obj)))

        # This version uses a generator expression to avoid computing a full
        # list only to immediately walk it again:
        filtered_values = (filter_nones(j) for j in obj)
        return [i for i in filtered_values if i is not None]
    elif isinstance(obj, dict):
        filtered_items = ((i, filter_nones(j)) for i, j in obj.items())
        return {k: v for k, v in filtered_items if v is not None}
    else:
        return obj


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
            display_name = new_item['display_name'] if 'display_name' in new_item and new_item['display_name'] != '' else new_item['name']
            latest = new_item['latest']
            previous = old_data_dict.get(name)

            if previous != latest:
                updates.append((display_name, latest, previous if previous is not None else ""))
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

    new_all_json = sorted(filter_nones(data), key=lambda x: x['name'])

    with open(p.joinpath('all.json'), 'w', encoding='utf-8') as f:
        b = json.dumps(new_all_json, ensure_ascii=True, separators=(',', ':'))
        f.write(b)

        with zstd.open(p.joinpath('all.json.zst'), 'wb') as zstf:
            zstf.write(b.encode('utf-8'))

    logger.info('The all.json file has been generated.')

    # Compare the new and old data and print the differences.
    differences = compare_json_data(new_all_json, old_all_json)

    if differences:
        logger.info('The following differences were found:')

        email_data = []

        for name, latest, previous in differences:
            email_data.append({'name': name, 'latest': latest, 'previous': previous})

            logger.info(f'{name}: {previous} -> {latest}')

        with open(Path(cfg.workdir).joinpath('email_notify.j2'), 'r', encoding='utf-8') as f:
            html_template = f.read()
            template = Template(html_template)
            html_content = template.render(items=email_data)

            ok_email = send_mail(
                to=['codeplus@qq.com'],
                subject='Github Notification from version-checker',
                content='No Content',
                html=html_content
            )

            logger.info(f'Send email result: {ok_email}')
    else:
        logger.info('No differences were found.')
