from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    """Класс, тестирующий контент."""

    NOTES_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.first_user = User.objects.create(username='Один пользователь')
        cls.second_user = User.objects.create(username='Второй пользователь')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Просто текст.',
            author=cls.first_user
        )

        Note.objects.bulk_create(
            Note(
                title=f'Заметка {index}',
                text='Просто текст.',
                author=cls.first_user,
                slug=f'zametka-{index}'
            )
            for index in range(10)
        )

        Note.objects.bulk_create(
            Note(
                title=f'Заметка {index}',
                text='Просто текст.',
                author=cls.second_user,
                slug=f'zametka-{index}'
            )
            for index in range(10, 20)
        )

    def test_note_context(self):
        """
        Отдельная заметка передаётся на страницу со списком заметок
        в списке object_list в словаре context.
        В список заметок одного пользователя не попадают
        заметки другого пользователя.
        """
        self.client.force_login(self.first_user)
        response = self.client.get(self.NOTES_URL)
        notes = response.context['note_list']
        self.assertIn(self.note, notes)
        author_list = [note.author for note in notes]
        self.assertNotIn(self.second_user, author_list)

    def test_form_in_add_edit(self):
        """На страницы создания и редактирования заметки передаются формы."""
        self.client.force_login(self.first_user)

        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
