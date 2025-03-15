from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


# Константы для страниц
HOME = pytest.lazy_fixture('home_url')
NEWS_DETAIL = pytest.lazy_fixture('news_detail_url')
COMMENT_EDIT = pytest.lazy_fixture('comment_edit_url')
COMMENT_DELETE = pytest.lazy_fixture('comment_delete_url')
LOGIN = pytest.lazy_fixture('login_url')
LOGOUT = pytest.lazy_fixture('logout_url')
SIGNUP = pytest.lazy_fixture('signup_url')
# Константы для клиента, через который делается запрос
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
READER_CLIENT = pytest.lazy_fixture('reader_client')
CLIENT = pytest.lazy_fixture('client')


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (HOME, CLIENT, HTTPStatus.OK),
        (NEWS_DETAIL, CLIENT, HTTPStatus.OK),
        (LOGIN, CLIENT, HTTPStatus.OK),
        (LOGOUT, CLIENT, HTTPStatus.OK),
        (SIGNUP, CLIENT, HTTPStatus.OK),
        (COMMENT_EDIT, READER_CLIENT, HTTPStatus.NOT_FOUND),
        (COMMENT_EDIT, AUTHOR_CLIENT, HTTPStatus.OK),
        (COMMENT_DELETE, READER_CLIENT, HTTPStatus.NOT_FOUND),
        (COMMENT_DELETE, AUTHOR_CLIENT, HTTPStatus.OK)
    ),
)
def test_availability_for_different_users(
        url, parametrized_client, expected_status
):
    """
    Проверка доступности страниц проекта для анонимных
    и авторизованных пользоваелей.
    """
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (COMMENT_EDIT, COMMENT_DELETE)
)
def test_redirects(client, url, login_url, comment_list):
    """
    При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
