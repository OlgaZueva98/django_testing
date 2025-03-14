from .config import BaseFixtures
from notes.forms import NoteForm


class TestContent(BaseFixtures):
    """Класс, тестирующий контент."""

    def test_note_in_context(self):
        """
        Отдельная заметка передаётся на страницу со списком заметок
        в списке object_list в словаре context.
        """
        response = self.author_client.get(self.NOTES_URL)
        notes = response.context['note_list']
        self.assertIn(self.note, notes)

    def test_author_notes_not_in_readers_list(self):
        """
        В список заметок одного пользователя не попадают
        заметки другого пользователя.
        """
        response = self.author_client.get(self.NOTES_URL)
        notes = response.context['note_list']
        author_list = [note.author for note in notes]
        self.assertNotIn(self.reader, author_list)

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
