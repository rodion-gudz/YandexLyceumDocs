import argparse
import os
import shutil

from jinja2 import Environment, FileSystemLoader
from tqdm import tqdm

from generator.client import Client

env = Environment(loader=FileSystemLoader('templates'),
                  trim_blocks=True,
                  lstrip_blocks=True)

courses_template = env.get_template('courses.jinja2')
materials_template = env.get_template('materials.jinja2')
material_template = env.get_template('material.jinja2')
lessons_template = env.get_template('lessons.jinja2')

parser = argparse.ArgumentParser(description="yandex lyceum docs generator")
parser.add_argument('--login', type=str, required=True)
parser.add_argument('--password', type=str, required=True)
args = parser.parse_args()

client = Client(login=args.login,
                password=args.password)
courses = client.get_courses()
print("Список курсов:")
courses = [course for course in courses if input(f"{course['title']}\t(Y/n) ").lower().strip() in ('Y', '')]

if os.path.exists('docs'):
    shutil.rmtree('docs')

os.makedirs("docs/courses")


def save_courses_page(courses):
    with open(os.path.join('docs', 'index.html'), "w") as fh:
        fh.write(courses_template.render(courses=courses))


def save_lesson_page(materials, course_id, lesson_id):
    lesson_path = os.path.join('docs', 'courses', str(course_id), 'lessons', str(lesson_id))
    os.mkdir(lesson_path)
    with open(os.path.join(lesson_path, 'index.html'), "w") as fh:
        fh.write(materials_template.render(materials=materials))


def save_material_page(content, shortTitle, title, course_id, lesson_id, material_id):
    material_path = os.path.join('docs', 'courses', str(course_id), 'lessons', str(lesson_id), 'materials',
                                 str(material_id))
    os.mkdir(material_path)
    with open(os.path.join(material_path, 'index.html'), "w") as fh:
        fh.write(material_template.render(
            content=content or "",
            shortTitle=shortTitle,
            title=title))


print()
print("Скачивание курсов...")
for course in courses:
    lessons = client.get_course(course['course_id'], course['group_id'])
    os.makedirs(f"docs/courses/{course['course_id']}/lessons")
    for lesson in tqdm(lessons,
                       unit='course',
                       bar_format='{l_bar}{bar}| [{remaining}]',
                       desc=course['title']):
        if not isinstance(lesson, dict) or lesson['type'] != 'normal':
            continue
        materials = client.get_materials_id(lesson['id'])
        lesson['has_materials'] = bool(materials)
        if not materials:
            continue
        save_lesson_page(materials, course['course_id'], lesson['id'])
        os.mkdir(f"docs/courses/{course['course_id']}/lessons/{lesson['id']}/materials")
        for material in materials:
            material = client.get_material(lesson['id'], course['group_id'], material['id'])
            if 'detailedMaterial' not in material:
                continue

            save_material_page(material['detailedMaterial']['content'], material['lesson']['shortTitle'],
                               material['detailedMaterial']['title'],
                               course['course_id'], lesson['id'], material['detailedMaterial']['id'])

    output_from_parsed_template = lessons_template.render(
        lessons=lessons,
        title=course['title'])
    with open(f"docs/courses/{course['course_id']}/index.html", "w") as fh:
        fh.write(output_from_parsed_template)
    if not lessons:
        courses.remove(course)

save_courses_page(courses)
