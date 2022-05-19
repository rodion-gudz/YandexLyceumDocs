import argparse
import os
import shutil

from jinja2 import Environment, FileSystemLoader
from tqdm import tqdm

from generator.client import Client

env = Environment(
    loader=FileSystemLoader("templates"), trim_blocks=True, lstrip_blocks=True
)

courses_template = env.get_template("courses.jinja2")
lesson_template = env.get_template("lesson.jinja2")
material_template = env.get_template("material.jinja2")
task_template = env.get_template("task.jinja2")
lessons_template = env.get_template("lessons.jinja2")

parser = argparse.ArgumentParser(description="yandex lyceum docs generator")
parser.add_argument("--login", type=str, required=True)
parser.add_argument("--password", type=str, required=True)
args = parser.parse_args()

client = Client(login=args.login, password=args.password)
courses = client.get_courses()
print("Список курсов:")
courses = [
    course
    for course in courses
    if input(f"{course['title']}\t(Y/n) ").lower().strip() in ("y", "")
]

if os.path.exists("docs"):
    shutil.rmtree("docs")

os.makedirs(os.path.join("docs", "courses"))
shutil.copytree(os.path.join("templates", "css"), os.path.join("docs", "css"))
shutil.copytree(os.path.join("templates", "js"), os.path.join("docs", "js"))

sections_types = {
    "classwork": "Классная работа",
    "homework": "Домашняя работа",
    "additional": "Дополнительные задачи",
    "individual-work": "Самостоятельная работа",
    "control-work": "Контрольная работа",
}


def save_courses_page(courses):
    with open(os.path.join("docs", "index.html"), "w", encoding="utf-8") as fh:
        fh.write(courses_template.render(courses=courses))


def save_lesson_page(
    materials, course_id, lesson_id, lesson_tasks_ids, lesson_title, lesson_description
):
    lesson_path = os.path.join(
        "docs", "courses", str(course_id), "lessons", str(lesson_id)
    )
    os.mkdir(lesson_path)
    with open(os.path.join(lesson_path, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(
            lesson_template.render(
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
    task_id,
    title,
    lesson_short_title,
    task_type,
    task_title,
    task_description,
    lesson_tasks_ids,
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
                solution_code=solution_code,
                solution_url=solution_url,
            )
        )


print()
print("Скачивание курсов...")
for course in courses:
    course_id = course["course_id"]
    group_id = course["group_id"]
    course_title = course["title"]

    course_path = os.path.join("docs", "courses", str(course_id))
    lessons = client.get_course(course_id, group_id)
    if "code" in lessons and lessons["code"] == "403_course_view_permission_denied":
        course["active"] = False
        print(f"{course_title} не доступен")
        continue
    course["active"] = True
    lessons_path = os.path.join(course_path, "lessons")
    os.makedirs(lessons_path)
    for lesson in tqdm(
        lessons,
        unit="course",
        bar_format="{l_bar}{bar}| [{remaining}]",
        desc=course_title,
    ):

        lesson_tasks = client.get_tasks(course_id, lesson["id"], group_id)

        try:
            lesson_tasks_formatted = [
                {
                    "type": task_group["type"],
                    "full_type": sections_types[task_group["type"]],
                    "tasks": [
                        {"id": task["id"], "title": task["title"], "active": True}
                        for task in task_group["tasks"]
                    ],
                }
                for task_group in lesson_tasks
            ]
        except Exception:
            lesson_tasks_formatted = [
                {
                    "type": task_group["type"],
                    "full_type": "Вступительный тест",
                    "tasks": [
                        {"id": task["id"], "title": task["title"], "active": False}
                        for task in task_group["problems"]
                    ],
                }
                for task_group in lesson_tasks
            ]

        materials = client.get_materials_id(lesson["id"])

        if materials == 0:
            materials = None

        lesson_information = client.get_lesson_info(lesson["id"], course_id, group_id)

        save_lesson_page(
            materials,
            course_id,
            lesson["id"],
            lesson_tasks_formatted,
            lesson["title"],
            lesson_information["description"],
        )

        os.mkdir(os.path.join(lessons_path, str(lesson["id"]), "tasks"))

        for task_group in lesson_tasks_formatted:
            task_type = task_group["type"]
            tasks = task_group["tasks"]
            for task in tasks:
                task_info = client.get_task_information(group_id, task["id"])
                if "code" in task_info and task_info["code"] == "404_task_not_found":
                    continue
                solution_id = task_info["solutionId"]
                solution_info = client.get_solution(solution_id)
                if solution_info["solution"]["status"]["type"] != "new" and solution_info["solution"]["score"] != 0:
                    solution_url = solution_info["solution"]["latestSubmission"]["file"]["url"]
                    if "sourceCode" in solution_info["solution"]["latestSubmission"]["file"]:
                        solution_code = solution_info["solution"]["latestSubmission"]["file"]["sourceCode"].strip()
                    else:
                        solution_code = None
                else:
                    solution_code = None
                    solution_url = None
                save_task_page(
                    lesson_id=lesson["id"],
                    task_id=task["id"],
                    title=lesson["title"],
                    lesson_short_title=lesson["shortTitle"],
                    task_type=task_type,
                    task_title=task["title"],
                    task_description=task_info["description"],
                    lesson_tasks_ids=lesson_tasks_formatted,
                    solution_code=solution_code,
                    solution_url=solution_url,
                )

        if materials:
            os.mkdir(os.path.join(lessons_path, str(lesson["id"]), "materials"))
            for material in materials:
                material_id = material["id"]
                content = client.get_material(lesson["id"], group_id, material_id)
                if "detailedMaterial" not in content:
                    continue

                save_material_page(
                    content["detailedMaterial"]["content"],
                    content["lesson"]["shortTitle"],
                    content["detailedMaterial"]["title"],
                    course_id,
                    lesson["id"],
                    content["detailedMaterial"]["id"],
                )

    output_from_parsed_template = lessons_template.render(
        lessons=lessons, title=course_title
    )
    with open(os.path.join(course_path, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(output_from_parsed_template)
    if not lessons:
        courses.remove(course)

    save_courses_page(courses)
