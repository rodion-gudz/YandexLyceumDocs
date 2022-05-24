import os
import pickle

from requests import Session

from generator.errors import AuthError


class Client:
    def __init__(self, login, password):
        session = Session()
        if not os.path.exists("auth.session"):
            if (
                    session.post(
                        "https://passport.yandex.ru/passport?mode=auth",
                        data={"login": login, "passwd": password},
                    ).url
                    != "https://passport.yandex.ru/profile"
            ):
                raise AuthError(
                    "Ошибка авторизации (Неверные данные или включен 2FA)")
            with open("auth.session", "wb") as f:
                pickle.dump(session, f)
        else:
            with open("auth.session", "rb") as f:
                session = pickle.load(f)
        self.session = session

    def get_courses(self):
        profile_json = self.session.get(
            "https://lyceum.yandex.ru/api/profile",
            params={
                "onlyActiveCourses": True,
                "withCoursesSummary": True,
                "withExpelled": True,
            },
        ).json()

        if "code" in profile_json and profile_json["code"] == "401_unauthorized":
            return False

        return [
            {
                "title": course["title"],
                "course_id": course["id"],
                "group_id": course["group"]["id"],
            }
            for course in profile_json["coursesSummary"]["student"]
        ]

    def get_course(self, course_id, group_id):
        return self.session.get(
            f"https://lyceum.yandex.ru/api/student/lessons?courseId="
            f"{course_id}&groupId={group_id}"
        ).json()

    def get_lessons(self, course_id, group_id):
        return self.session.get(
            "https://lyceum.yandex.ru/api/student/lessons",
            params={"groupId": group_id, "courseId": course_id},
        ).json()

    def get_material(self, lesson_id, group_id, material_id):
        return self.session.get(
            f"https://lyceum.yandex.ru/api/student/materials/{material_id}",
            params={"groupId": group_id, "lessonId": lesson_id},
        ).json()

    def get_materials_id(self, lesson_id):
        url = "https://lyceum.yandex.ru/api/materials"
        if not (
                material_info := self.session.get(
                    url, params={"lessonId": lesson_id}
                ).json()
        ):
            return 0
        return [
            {"id": material["id"], "title": material["title"]}
            for material in material_info
            if material["type"] == "textbook"
        ]

    def get_task_information(self, group_id, task_id):
        return self.session.get(
            f"https://lyceum.yandex.ru/api/student/tasks/{task_id}",
            params={"groupId": group_id},
        ).json()

    def get_tasks(self, course_id, lesson_id, group_id):
        return self.session.get(
            "https://lyceum.yandex.ru/api/student/lessonTasks",
            params={"courseId": course_id, "groupId": group_id,
                    "lessonId": lesson_id},
        ).json()

    def get_lesson_info(self, lesson_id, course_id, group_id):
        return self.session.get(
            f"https://lyceum.yandex.ru/api/student/lessons/{lesson_id}",
            params={"courseId": course_id, "groupId": group_id},
        ).json()

    def get_solution(self, solution_id):
        return self.session.get(
            f"https://lyceum.yandex.ru/api/student/solutions/{solution_id}"
        ).json()
