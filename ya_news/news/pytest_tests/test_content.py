import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client):
    """Количество новостей на главной странице — не более 10."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count <= settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client):
    """Новости отсортированы от самой свежей к самой старой."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, id_for_news):
    """
    Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке.
    """
    url = reverse('news:detail', args=id_for_news)
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'parametrized_client, form_in_context.',
    (
        (pytest.lazy_fixture('reader_client'), True),
        (pytest.lazy_fixture('unauth_client'), False),
    )
)
def test_comment_form_in_context(
    parametrized_client, form_in_context, id_for_news
):
    """
    Анонимному пользователю недоступна форма для отправки комментария
    на странице отдельной новости, а авторизованному доступна.
    """
    url = reverse('news:detail', args=id_for_news)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_context
    if 'form' in response.context:
        assert isinstance(response.context['form'], CommentForm)
