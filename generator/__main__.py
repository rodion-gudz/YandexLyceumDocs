import os
import shutil

from PyYandexLMS.synchronous.client import Client
from tqdm import tqdm

from generator.args import parse_arguments
from generator.render import render_page
from generator.stuff import sections_types
from generator.templates import (
    courses_template,
    lesson_template,
    lessons_template,
    material_template,
    problem_template,
    task_template,
)
from generator.utils import get_neighboring_items, parse_resources_and_paragraph

args = parse_arguments()

client = Client(login=args.login, password=args.password)

user = client.get_user(with_parents=False, with_children=False)

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

        if args.materials:
            materials = client.get_materials(
                lesson_id=lesson.id,
            )
        else:
            materials = None

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

        if task_groups and any(task_group.tasks for task_group in task_groups):

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

                        if args.solutions:
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
                        else:
                            solution_code = None
                            solution_url = None

                        previous_id, next_id = get_neighboring_items(
                            items=task_ids,
                            item=task.id,
                        )

                        render_page(
                            path=[tasks_path, str(task.id)],
                            template=task_template,
                            previous_task_id=previous_id,
                            next_task_id=next_id,
                            lesson=lesson,
                            task=task,
                            task_info=task_info,
                            task_group=task_group,
                            task_groups=task_groups,
                            add_solution=args.solutions,
                            solution_code=solution_code,
                            solution_url=solution_url,
                            sections_types=sections_types,
                        )

        if task_groups and any(task_group.problems for task_group in task_groups):

            problems_path = os.path.join(lesson_path, "problems")
            os.mkdir(problems_path)

            problems_id = []
            for task_group in task_groups:
                if task_group.problems:
                    problems_id.extend(task.id for task in task_group.problems)

            for task_group in task_groups:
                if task_group.problems:
                    for problem in task_group.problems:

                        previous_id, next_id = get_neighboring_items(
                            items=problems_id,
                            item=problem.id,
                        )

                        paragraphs = []
                        for layout in problem.problem.markup.layout:
                            resources_id, text = parse_resources_and_paragraph(
                                layout.content.text or ""
                            )
                            paragraphs.append(
                                {"text": text, "resources_id": resources_id}
                            )

                        render_page(
                            path=[problems_path, str(problem.id)],
                            template=problem_template,
                            lesson=lesson,
                            problem=problem,
                            task_group=task_group,
                            task_groups=task_groups,
                            paragraphs=paragraphs,
                            resources=problem.problem.resources,
                            next_id=next_id,
                            previous_id=previous_id,
                            sections_types=sections_types,
                        )

        if (
            args.materials
            and materials
            and any(material.type == "textbook" for material in materials)
        ):

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
