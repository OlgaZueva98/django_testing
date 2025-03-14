from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_user_can_create_comment(
    author_client,
    author,
    form_data,
    id_for_news,
    url_for_comments
):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=id_for_news)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, url_for_comments)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.latest('created')
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, id_for_news):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=id_for_news)
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_use_bad_words(reader_client, id_for_news):
    """
    Rомментарий, который содержит запрещённые слова, не будет опубликован,
    а форма вернёт ошибку.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=id_for_news)
    response = reader_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client,
    form_data,
    comment,
    id_for_comment,
    url_for_comments
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    url = reverse('news:edit', args=id_for_comment)
    response = author_client.post(url, form_data)
    assertRedirects(response, url_for_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_reader_cant_edit_comment(
    reader_client,
    form_data,
    comment,
    id_for_comment
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    url = reverse('news:edit', args=id_for_comment)
    response = reader_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=id_for_comment[0])
    assert comment.text == comment_from_db.text


@pytest.mark.django_db
def test_author_can_delete_comment(
    author_client,
    id_for_comment,
    url_for_comments
):
    """Авторизованный пользователь может удалять свои комментарии."""
    url = reverse('news:delete', args=id_for_comment)
    response = author_client.post(url)
    assertRedirects(response, url_for_comments)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_reader_cant_delete_comment(reader_client, id_for_comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    url = reverse('news:delete', args=id_for_comment)
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
