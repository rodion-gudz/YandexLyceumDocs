from generator.stuff import sections_types


def format_lesson_tasks(lesson_tasks):
    try:
        formatted_tasks = [
            {
                "type": group["type"],
                "full_type": sections_types[group["type"]],
                "tasks": [
                    {"id": task["id"], "title": task["title"], "active": True}
                    for task in group["tasks"]
                ],
            }
            for group in lesson_tasks
        ]
    except Exception:
        formatted_tasks = [
            {
                "type": group["type"],
                "full_type": "Вступительный тест",
                "tasks": [
                    {"id": task["id"], "title": task["title"], "active": False}
                    for task in group["problems"]
                ],
            }
            for group in lesson_tasks
        ]

    return formatted_tasks


def prepare_materials(client, arg, lesson_id):
    if arg:
        add_materials = True

        materials = client.get_materials_id(lesson_id)

        if materials == 0:
            materials = None
    else:
        add_materials = False
        materials = None

    return add_materials, materials
