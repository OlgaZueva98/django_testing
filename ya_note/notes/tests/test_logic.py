from http import HTTPStatus

from pytils.translit import slugify

from .config import BaseFixtures
from notes.forms import WARNING
from notes.models import Note


class TestNoteCreation(BaseFixtures):
    """Класс, тестирующий создание заметки."""

    @classmethod
    def setUpTestData(cls):
        super(TestNoteCreation, cls).setUpTestData()
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT
        }

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        prev_notes_count = Note.objects.count()
        self.client.post(self.NOTE_ADD_URL, data=self.form_data)
        cur_notes_count = Note.objects.count()
        self.assertEqual(cur_notes_count, prev_notes_count)

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        Note.objects.all().delete()
        self.author_client.post(self.NOTE_ADD_URL, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.author)

    def test_note_has_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        prev_notes_count = Note.objects.count()
        response = self.author_client.post(
            self.NOTE_ADD_URL,
            data=self.form_data
        )
        cur_notes_count = Note.objects.count()
        self.assertEqual(cur_notes_count, prev_notes_count)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.note.slug + WARNING)
        )

    def test_autocreate_slug_if_not_exist(self):
        """Slug формируется автоматически из заголовка."""
        Note.objects.all().delete()
        self.author_client.post(self.NOTE_ADD_URL, data=self.form_data)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.slug, slugify(self.NOTE_TITLE)[:100])


class TestNoteEditDelete(BaseFixtures):
    """Класс, тестирующий редактирование и удаление заметки."""

    @classmethod
    def setUpTestData(cls):
        super(TestNoteEditDelete, cls).setUpTestData()
        cls.form_data = {'title': cls.NOTE_TITLE, 'text': cls.NEW_NOTE_TEXT}

    def test_author_can_delete_note(self):
        """Пользователь может удалять свои заметки."""
        prev_notes_count = Note.objects.count()
        response = self.author_client.delete(self.NOTE_DELETE_URL)
        self.assertRedirects(response, self.SUCCESS_URL)
        cur_notes_count = Note.objects.count()
        self.assertEqual(cur_notes_count, prev_notes_count - 1)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалять чужие заметки."""
        prev_notes_count = Note.objects.count()
        response = self.reader_client.delete(self.NOTE_DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        cur_notes_count = Note.objects.count()
        self.assertEqual(cur_notes_count, prev_notes_count)

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        response = self.author_client.post(
            self.NOTE_EDIT_URL,
            data=self.form_data
        )
        self.assertRedirects(response, self.SUCCESS_URL)
        new_note = Note.objects.get(id=self.note.id)
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.title, self.note.title)
        self.assertEqual(new_note.author, self.note.author)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать чужие заметки."""
        response = self.reader_client.post(
            self.NOTE_EDIT_URL,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        new_note = Note.objects.get(id=self.note.id)
        self.assertEqual(new_note.text, self.note.text)
        self.assertEqual(new_note.title, self.note.title)
        self.assertEqual(new_note.author, self.note.author)
