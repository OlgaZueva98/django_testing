from http import HTTPStatus

from .config import BaseFixtures


class TestRoutes(BaseFixtures):
    """Класс, тестирующий маршруты."""

    def test_pages_availability_for_different_users(self):
        """
        Проверка доступности страниц проекта для анонимных
        и авторизованных пользоваелей.
        """
        test_cases = (
            (self.HOME_URL, self.client, HTTPStatus.OK),
            (self.LOGIN_URL, self.client, HTTPStatus.OK),
            (self.LOGOUT_URL, self.client, HTTPStatus.OK),
            (self.SIGNUP_URL, self.client, HTTPStatus.OK),
            (self.NOTES_URL, self.reader_client, HTTPStatus.OK),
            (self.SUCCESS_URL, self.reader_client, HTTPStatus.OK),
            (self.NOTE_ADD_URL, self.reader_client, HTTPStatus.OK),
            (self.NOTE_DETAIL_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.NOTE_DETAIL_URL, self.author_client, HTTPStatus.OK),
            (self.NOTE_EDIT_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.NOTE_EDIT_URL, self.author_client, HTTPStatus.OK),
            (self.NOTE_DELETE_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.NOTE_DELETE_URL, self.author_client, HTTPStatus.OK)
        )

        for url, client, expected_status in test_cases:
            with self.subTest(name=url):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        """Проверяет редиректы для анонимных пользователей."""
        urls = (
            self.NOTES_URL,
            self.SUCCESS_URL,
            self.NOTE_ADD_URL,
            self.NOTE_EDIT_URL,
            self.NOTE_DELETE_URL
        )

        for url in urls:
            with self.subTest(name=url):
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
