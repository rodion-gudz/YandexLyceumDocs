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

os.makedirs(os.path.join('docs', 'courses'))


def save_courses_page(courses):
    with open(os.path.join('docs', 'index.html'), "w", encoding=('windows-1252' if os.name == 'nt' else 'utf-8')) as fh:
        fh.write(courses_template.render(courses=courses))


def save_lesson_page(materials, course_id, lesson_id):
    lesson_path = os.path.join('docs', 'courses', str(course_id), 'lessons', str(lesson_id))
    os.mkdir(lesson_path)
    with open(os.path.join(lesson_path, 'index.html'), "w", encoding=('windows-1252' if os.name == 'nt' else 'utf-8')) as fh:
        fh.write(materials_template.render(materials=materials))


def save_material_page(content, shortTitle, title, course_id, lesson_id, material_id):
    material_path = os.path.join('docs', 'courses', str(course_id), 'lessons', str(lesson_id), 'materials',
                                 str(material_id))
    os.mkdir(material_path)
    with open(os.path.join(material_path, 'index.html'), "w", encoding=('windows-1252' if os.name == 'nt' else 'utf-8')) as fh:
        fh.write(material_template.render(
            content=content or "",
            shortTitle=shortTitle,
            title=title))


print()
print("Скачивание курсов...")
for course in courses:
    course_id = course['course_id']
    group_id = course['group_id']
    course_title = course['title']

    course_path = os.path.join('docs', 'courses', str(course_id))
    lessons = client.get_course(course_id, group_id)
    lessons_path = os.path.join(course_path, 'lessons')
    os.makedirs(lessons_path)
    for lesson in tqdm(lessons,
                       unit='course',
                       bar_format='{l_bar}{bar}| [{remaining}]',
                       desc=course_title):
        if not isinstance(lesson, dict) or lesson['type'] != 'normal':
            continue
        materials = client.get_materials_id(lesson['id'])
        lesson['has_materials'] = bool(materials)
        if not materials:
            continue
        save_lesson_page(materials, course_id, lesson['id'])
        os.mkdir(os.path.join(lessons_path, str(lesson['id']), 'materials'))
        for material in materials:
            material_id = material['id']
            content = client.get_material(lesson['id'], group_id, material_id)
            if 'detailedMaterial' not in content:
                continue

            save_material_page(content['detailedMaterial']['content'], content['lesson']['shortTitle'],
                               content['detailedMaterial']['title'],
                               course_id, lesson['id'], content['detailedMaterial']['id'])

    output_from_parsed_template = lessons_template.render(
        lessons=lessons,
        title=course_title)
    with open(os.path.join(course_path, 'index.html'), "w", encoding=('windows-1252' if os.name == 'nt' else 'utf-8')) as fh:
        fh.write(output_from_parsed_template)
    if not lessons:
        courses.remove(course)

    save_courses_page(courses)
