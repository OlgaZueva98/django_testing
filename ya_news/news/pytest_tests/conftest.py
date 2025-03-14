import pytest

from django.test.client import Client
from django.urls import reverse

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def unauth_client():
    return Client()


@pytest.fixture
def news(author):
    return News.objects.create(
        title='Заголовок',
        text='Текст новости'
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def id_for_news(news):
    return (news.id,)


@pytest.fixture
def id_for_comment(comment):
    return (comment.id,)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }


@pytest.fixture
def url_for_comments(id_for_news):
    url = reverse('news:detail', args=id_for_news)
    return f'{url}#comments'
