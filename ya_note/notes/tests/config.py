from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseFixtures(TestCase):
    # Константы для страниц
    SLUG = ('zametka',)
    LOGIN_URL = reverse('users:login')
    LOGOUT_URL = reverse('users:logout')
    SIGNUP_URL = reverse('users:signup')
    SUCCESS_URL = reverse('notes:success')
    HOME_URL = reverse('notes:home')
    NOTES_URL = reverse('notes:list')
    NOTE_DETAIL_URL = reverse('notes:detail', args=SLUG)
    NOTE_ADD_URL = reverse('notes:add')
    NOTE_EDIT_URL = reverse('notes:edit', args=SLUG)
    NOTE_DELETE_URL = reverse('notes:delete', args=SLUG)
    # Константы для заметки
    NOTE_TITLE = 'Заметка'
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённый текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Авторизованный автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Авторизованный читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug=cls.SLUG[0]
        )
