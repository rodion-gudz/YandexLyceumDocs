import os

from jinja2 import Environment, FileSystemLoader
from generator.stuff import sections_types


def save_courses_page(courses):
    with open(os.path.join("docs", "index.html"), "w", encoding="utf-8") as fh:
        fh.write(courses_template.render(courses=courses))


def save_lesson_page(
    add_materials, materials, course_id, lesson_id, lesson_tasks_ids, lesson_title, lesson_description
):
    lesson_path = os.path.join(
        "docs", "courses", str(course_id), "lessons", str(lesson_id)
    )
    os.mkdir(lesson_path)
    with open(os.path.join(lesson_path, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(
            lesson_template.render(
                add_materials=add_materials,
                materials=materials,
                task_groups=lesson_tasks_ids,
                lesson_titletle=lesson_title,
                lesson_description=lesson_description,
            )
        )


def save_material_page(content, short_title, title, course_id, lesson_id, material_id):
    material_path = os.path.join(
        "docs",
        "courses",
        str(course_id),
        "lessons",
        str(lesson_id),
        "materials",
        str(material_id),
    )
    os.mkdir(material_path)
    with open(os.path.join(material_path, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(
            material_template.render(
                content=content or "", short_title=short_title, title=title
            )
        )


def save_task_page(
    lesson_id,
    course_id,
    task_id,
    title,
    lesson_short_title,
    task_type,
    task_title,
    task_description,
    lesson_tasks_ids,
    add_solution,
    solution_code,
    solution_url
):
    task_path = os.path.join(
        "docs",
        "courses",
        str(course_id),
        "lessons",
        str(lesson_id),
        "tasks",
        str(task_id),
    )
    os.mkdir(task_path)

    task_ids = []
    for task_group in lesson_tasks_ids:
        task_ids.extend(task["id"] for task in task_group["tasks"])

    task_index = task_ids.index(task_id)
    if task_index == 0:
        previous_task_id = None
    else:
        previous_task_id = task_ids[task_ids.index(task_id) - 1]
    if task_index == len(task_ids) - 1:
        next_task_id = None
    else:
        next_task_id = task_ids[task_ids.index(task_id) + 1]

    with open(os.path.join(task_path, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(
            task_template.render(
                title=title,
                lesson_short_title=lesson_short_title,
                previous_task_id=previous_task_id,
                next_task_id=next_task_id,
                task_type=task_type,
                task_type_title=sections_types[task_type],
                task_title=task_title,
                task_description=task_description,
                task_groups=lesson_tasks_ids,
                task_id=task_id,
                add_solution=add_solution,
                solution_code=solution_code,
                solution_url=solution_url,
            )
        )


env = Environment(
    loader=FileSystemLoader("templates"), trim_blocks=True, lstrip_blocks=True
)
courses_template = env.get_template("courses.jinja2")
lesson_template = env.get_template("lesson.jinja2")
material_template = env.get_template("material.jinja2")
task_template = env.get_template("task.jinja2")
lessons_template = env.get_template("lessons.jinja2")
