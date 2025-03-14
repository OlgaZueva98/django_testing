import pytest
from django.conf import settings

from news.forms import CommentForm


def test_news_count(client, home_url, news_list):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count <= settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, home_url, news_list):
    """Новости отсортированы от самой свежей к самой старой."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news_detail_url, comment_list):
    """
    Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке.
    """
    response = client.get(news_detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (pytest.lazy_fixture('reader_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_comment_form_in_context(
        parametrized_client,
        form_in_context,
        news_detail_url
):
    """
    Анонимному пользователю недоступна форма для отправки комментария
    на странице отдельной новости, а авторизованному доступна.
    """
    response = parametrized_client.get(news_detail_url)
    form = response.context.get('form')
    assert isinstance(form, CommentForm) == form_in_context
