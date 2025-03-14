from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('id_for_news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_home_availability_for_anonymous_user(client, name, args, news):
    """
    Главная страница, страница отдельной новости,
    cтраницы регистрации пользователей, входа в учётную запись и выхода
    из неё доступны анонимному пользователю.
    """
    url = reverse(name, args=args)
    print('URL', url)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_for_comment')),
        ('news:delete', pytest.lazy_fixture('id_for_comment')),
    ),
)
def test_edit_delete_for_different_users(
        parametrized_client, name, args, expected_status
):
    """
    Cтраницы удаления и редактирования комментария доступны автору комментария.
    Авторизованный пользователь не может зайти на страницы редактирования
    или удаления чужих комментариев.
    """
    url = reverse(name, args=args)
    response = parametrized_client.get(url)

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_for_comment')),
        ('news:delete', pytest.lazy_fixture('id_for_comment'))
    ),
)
def test_redirects(client, name, args):
    """
    При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    login_url = reverse('users:login')
    if args:
        url = reverse(name, args=args)
    else:
        url = reverse(name)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
