from jinja2 import Environment, FileSystemLoader

env = Environment(
    loader=FileSystemLoader("templates"), trim_blocks=True, lstrip_blocks=True
)
courses_template = env.get_template("courses.jinja2")
lesson_template = env.get_template("lesson.jinja2")
material_template = env.get_template("material.jinja2")
task_template = env.get_template("task.jinja2")
problem_template = env.get_template("problem.jinja2")
lessons_template = env.get_template("lessons.jinja2")
