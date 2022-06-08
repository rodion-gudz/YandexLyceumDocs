import os
from typing import List, Union

from jinja2 import Template


def render_page(path: List[Union[str, bytes]], template: Template, **kwargs):
    save_path = os.path.join(*path)

    os.mkdir(save_path)

    with open(os.path.join(save_path, "index.html"), "w", encoding="utf-8") as file:
        file.write(template.render(**kwargs))
