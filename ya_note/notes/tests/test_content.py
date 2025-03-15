from .config import BaseFixtures
from notes.forms import NoteForm


class TestContent(BaseFixtures):
    """Класс, тестирующий контент."""

    def test_note_is_in_context(self):
        """
        Отдельная заметка передаётся на страницу со списком заметок
        в списке object_list в словаре context.
        В список заметок одного пользователя не попадают
        заметки другого пользователя.
        """
        test_cases = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for client, expected_result in test_cases:
            response = client.get(self.NOTES_URL)
            notes = response.context['note_list']
            self.assertIs((self.note in notes), expected_result)

    def test_form_in_add_edit(self):
        """На страницы создания и редактирования заметки передаются формы."""
        urls = (
            self.NOTE_ADD_URL,
            self.NOTE_EDIT_URL,
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.author_client.get(url)
                form = response.context.get('form')
                self.assertIsInstance(form, NoteForm)
