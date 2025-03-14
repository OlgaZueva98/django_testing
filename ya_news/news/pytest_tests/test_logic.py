from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


BAD_WORDS_DATA = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}


@pytest.mark.django_db
def test_user_can_create_comment(
        author_client,
        author,
        form_data,
        news_detail_url,
        url_for_comments
):
    """Авторизованный пользователь может отправить комментарий."""
    response = author_client.post(news_detail_url, data=form_data)
    assertRedirects(response, url_for_comments)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.latest('created')
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client,
        form_data,
        news_detail_url
):
    """Анонимный пользователь не может отправить комментарий."""
    client.post(news_detail_url, data=form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_use_bad_words(reader_client, news_detail_url):
    """
    Rомментарий, который содержит запрещённые слова, не будет опубликован,
    а форма вернёт ошибку.
    """
    response = reader_client.post(news_detail_url, data=BAD_WORDS_DATA)
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
        comment_edit_url,
        url_for_comments
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    response = author_client.post(comment_edit_url, form_data)
    assertRedirects(response, url_for_comments)
    new_comment = Comment.objects.get(id=comment.id)
    assert new_comment.text == form_data['text']
    assert new_comment.created == comment.created
    assert new_comment.news == comment.news
    assert new_comment.author == comment.author


@pytest.mark.django_db
def test_reader_cant_edit_comment(
        reader_client,
        form_data,
        comment,
        comment_edit_url
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    response = reader_client.post(comment_edit_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.created == comment_from_db.created
    assert comment.news == comment_from_db.news
    assert comment.author == comment_from_db.author


@pytest.mark.django_db
def test_author_can_delete_comment(
        author_client,
        comment_delete_url,
        url_for_comments
):
    """Авторизованный пользователь может удалять свои комментарии."""
    response = author_client.post(comment_delete_url)
    assertRedirects(response, url_for_comments)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_reader_cant_delete_comment(reader_client, comment_delete_url):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    response = reader_client.post(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
