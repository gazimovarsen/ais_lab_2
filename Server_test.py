from locust import HttpUser, task, between, tag
import random


class EnglishGangUser(HttpUser):
    """
    Класс для эмуляции пользователя системы English Gang (только публичные запросы)
    """

    # Время ожидания между запросами (от 1 до 5 секунд)
    wait_time = between(1.0, 5.0)

    def on_start(self):
        """Действия при старте тестирования - открытие главной страницы"""
        self.client.get("/")

    # GET запросы (публичные)
    @tag("get")
    @task(5)
    def get_public_teachers(self):
        """Тест GET-запроса для получения публичного списка преподавателей"""
        with self.client.get(
            "/api/teachers/public", catch_response=True, name="GET public teachers"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Ошибка получения списка преподавателей: {response.status_code}"
                )

    @tag("get")
    @task(3)
    def visit_homepage(self):
        """Тест GET-запроса для главной страницы"""
        with self.client.get("/", catch_response=True, name="GET homepage") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Ошибка доступа к главной странице: {response.status_code}"
                )

    @tag("get")
    @task(2)
    def visit_team_page(self):
        """Тест GET-запроса для страницы команды"""
        with self.client.get(
            "/team.html", catch_response=True, name="GET team page"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Ошибка доступа к странице команды: {response.status_code}"
                )

    @tag("get")
    @task(2)
    def visit_projects_page(self):
        """Тест GET-запроса для страницы проектов"""
        with self.client.get(
            "/projects.html", catch_response=True, name="GET projects page"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Ошибка доступа к странице проектов: {response.status_code}"
                )

    @tag("get")
    @task(2)
    def visit_technical_page(self):
        """Тест GET-запроса для технической страницы"""
        with self.client.get(
            "/technical.html", catch_response=True, name="GET technical page"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Ошибка доступа к технической странице: {response.status_code}"
                )

    @tag("get")
    @task(1)
    def visit_login_page(self):
        """Тест GET-запроса для страницы входа"""
        with self.client.get(
            "/login2.html", catch_response=True, name="GET login page"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Ошибка доступа к странице входа: {response.status_code}"
                )
