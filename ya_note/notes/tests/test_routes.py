from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Класс, тестирующий маршруты."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Авторизованный автор')
        cls.reader = User.objects.create(username='Авторизованный читатель')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Просто текст.',
            author=cls.author
        )

    def test_home_page(self):
        """
        Главная страница, страницы регистрации пользователей,
        входа в учётную запись и выхода из неё доступны всем пользователям.
        """
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup'
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """
        Страницы со списком заметок, успешного добавления заметки,
        добавления новой заметки доступны аутентифицированному пользователю.
        """
        urls = (
            'notes:list',
            'notes:success',
            'notes:add'
        )
        for name in urls:
            self.client.force_login(self.reader)

            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_detail_edit_and_delete(self):
        """
        Страницы отдельной заметки, удаления и редактирования заметки
        доступны только автору заметки. Другому пользователю
        вернётся ошибка 404.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )

        for user, status in users_statuses:
            self.client.force_login(user)

            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверяет редиректы для анонимных пользователей."""
        login_url = reverse('users:login')

        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,))
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
