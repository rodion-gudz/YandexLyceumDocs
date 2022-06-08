import os
import shutil

from PyYandexLMS.synchronous.client import Client
from tqdm import tqdm

from generator.args import parse_arguments
from generator.render import render_page
from generator.stuff import sections_types
from generator.templates import (
    courses_template,
    lessons_template,
    lesson_template,
    task_template,
    material_template,
)

args = parse_arguments()

client = Client(login=args.login, password=args.password)

user = client.get_user(
    with_parents=False,
    with_children=False
)

courses = user.courses_summary.teacher if args.teacher else user.courses_summary.student

print("Список курсов:")

courses = [
    course
    for course in courses
    if course.is_active
    if input(f"{course.title}\t(Y/n) ").lower().strip() in ("y", "")
]

if not courses:
    print("Ни одного курса не выбрано")
    exit()

if os.path.exists("docs"):
    shutil.rmtree("docs")

docs_path = "docs"

render_page(
    path=[docs_path],
    template=courses_template,
    courses=courses,
)

shutil.copytree(os.path.join("templates", "css"), os.path.join(docs_path, "css"))
shutil.copytree(os.path.join("templates", "js"), os.path.join(docs_path, "js"))

courses_path = os.path.join(docs_path, "courses")
os.mkdir(courses_path)

print("\nСкачивание курсов...")
for course in courses:
    course_path = os.path.join(courses_path, str(course.id))

    lessons = client.get_lessons_by_course(course=course)

    render_page(
        path=[course_path],
        template=lessons_template,
        lessons=lessons,
        title=course.title,
    )

    lessons_path = os.path.join(course_path, "lessons")
    os.makedirs(lessons_path)

    for lesson in tqdm(
        lessons,
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
        desc=course.title,
    ):
        lesson_path = os.path.join(lessons_path, str(lesson.id))

        task_groups = client.get_tasks(
            lesson_id=lesson.id,
            group_id=course.group.id,
            course_id=course.id,
        )

        materials = client.get_materials(
            lesson_id=lesson.id,
        )

        lesson_information = client.get_lesson(
            lesson_id=lesson.id,
            group_id=course.group.id,
            course_id=course.id,
        )

        render_page(
            path=[lessons_path, str(lesson.id)],
            template=lesson_template,
            lesson=lesson_information,
            add_materials=args.materials,
            materials=materials,
            task_groups=task_groups,
            sections_types=sections_types,
        )

        if task_groups:
            tasks_path = os.path.join(lesson_path, "tasks")
            os.mkdir(tasks_path)

            task_ids = []
            for task_group in task_groups:
                if task_group.tasks:
                    task_ids.extend(task.id for task in task_group.tasks)

            for task_group in task_groups:
                if task_group.tasks:
                    for task in task_group.tasks:

                        task_info = client.get_task(
                            task_id=task.id,
                            group_id=course.group.id,
                        )

                        solution_information = client.get_solution_information(
                            solution_id=task_info.solution_id,
                        )

                        if hasattr(
                            solution_information.solution.latest_submission, "file"
                        ):
                            solution_code = (
                                solution_information.solution.latest_submission.file.source_code
                            )
                            solution_url = (
                                solution_information.solution.latest_submission.file.url
                            )
                        else:
                            solution_code = None
                            solution_url = None

                        task_index = task_ids.index(task.id)
                        if task_index == 0:
                            previous_task_id = None
                        else:
                            previous_task_id = task_ids[task_ids.index(task.id) - 1]
                        if task_index == len(task_ids) - 1:
                            next_task_id = None
                        else:
                            next_task_id = task_ids[task_ids.index(task.id) + 1]

                        render_page(
                            path=[tasks_path, str(task.id)],
                            template=task_template,
                            previous_task_id=previous_task_id,
                            next_task_id=next_task_id,
                            lesson=lesson,
                            task=task,
                            task_info=task_info,
                            task_group=task_group,
                            task_groups=task_groups,
                            solution_code=solution_code,
                            solution_url=solution_url,
                            sections_types=sections_types,
                        )

        if materials:
            materials_path = os.path.join(lesson_path, "materials")
            os.mkdir(materials_path)

            for material in materials:
                if material.type != "textbook":
                    continue

                material_information = client.get_material(
                    material_id=material.id,
                    lesson_id=lesson.id,
                    group_id=course.group.id,
                )

                if not material_information.detailed_material:
                    continue

                render_page(
                    path=[materials_path, str(material.id)],
                    template=material_template,
                    lesson=lesson,
                    material=material_information.detailed_material,
                )
