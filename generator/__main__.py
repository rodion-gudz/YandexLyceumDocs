import argparse
import os
import shutil

from tqdm import tqdm

from generator.client import Client
from generator.docs_prepare import format_lesson_tasks, prepare_materials, \
    prepare_solution
from generator.page_savers import save_lesson_page, save_task_page, \
    save_material_page, save_courses_page, lessons_template

parser = argparse.ArgumentParser(description="yandex lyceum docs generator")
parser.add_argument("--login", type=str, required=True)
parser.add_argument("--password", type=str, required=True)
parser.add_argument('--materials', action="store_true")
parser.add_argument('--solutions', action="store_true")
parser.add_argument('--teacher', action="store_true")
args = parser.parse_args()

client = Client(login=args.login, password=args.password)
courses = client.get_courses("teacher" if args.teacher else "student")

if not courses:
    print("Нет доступа к yandex.lyceum.ru")
    exit()

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

print()
print("Скачивание курсов...")
for course in courses:
    course_id = course["course_id"]
    group_id = course["group_id"]
    course_title = course["title"]

    course_path = os.path.join("docs", "courses", str(course_id))
    lessons = client.get_course(course_id, group_id)
    if "code" in lessons and lessons["code"] \
            == "403_course_view_permission_denied":
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
        lesson_tasks_formatted = format_lesson_tasks(lesson_tasks)

        add_materials, materials = prepare_materials(client, args.materials,
                                                     lesson["id"])

        lesson_information = client.get_lesson_info(lesson["id"], course_id,
                                                    group_id)

        save_lesson_page(
            add_materials,
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
                if "code" in task_info and task_info["code"] \
                        == "404_task_not_found":
                    continue

                solution_id = task_info["solutionId"]
                add_solution, solution = args.solutions, prepare_solution(
                    client, solution_id)

                save_task_page(
                    lesson_id=lesson["id"],
                    course_id=course_id,
                    task_id=task["id"],
                    title=lesson["title"],
                    lesson_short_title=lesson["shortTitle"],
                    task_type=task_type,
                    task_title=task["title"],
                    task_description=task_info["description"],
                    lesson_tasks_ids=lesson_tasks_formatted,
                    add_solution=add_solution,
                    solution_code=solution["code"],
                    solution_url=solution["url"],
                )

        if materials:
            os.mkdir(os.path.join(lessons_path, str(lesson["id"]), "materials"))
            for material in materials:
                material_id = material["id"]
                content = client.get_material(lesson["id"], group_id,
                                              material_id)
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
    with open(os.path.join(course_path, "index.html"), "w",
              encoding="utf-8") as fh:
        fh.write(output_from_parsed_template)
    if not lessons:
        courses.remove(course)

    save_courses_page(courses)
