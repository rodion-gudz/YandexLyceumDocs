import re
from typing import List, Union


def get_neighboring_items(items: List[int], item: int) -> (int, int):
    item_index = items.index(item)

    previous_item = items[item_index - 1] if item_index != 0 else None
    next_item = items[item_index + 1] if item_index != len(items) - 1 else None

    return previous_item, next_item


def parse_resources_and_paragraph(text: str) -> (List[int], str):
    resource_regex = re.compile(r"resource:\d+")
    resources_id = []
    for resource in resource_regex.findall(text):
        text = re.sub(r"\{resource:\d+}", "", text)
        resources_id.append(resource.split(":")[1])

    return resources_id, text
