import tempfile

import pytest
from mixer.backend.django import mixer as _mixer
from posts.models import Post, Group


@pytest.fixture()
def mock_media(settings):
    with tempfile.TemporaryDirectory() as temp_directory:
        settings.MEDIA_ROOT = temp_directory
        yield temp_directory


@pytest.fixture
def mixer():
    return _mixer


@pytest.fixture
def post(user):
    image = tempfile.NamedTemporaryFile(suffix=".jpg").name
    return Post.objects.create(text='Тестовый пост 1', author=user, image=image)


@pytest.fixture
def group():
    return Group.objects.create(title='Тестовая группа 1', slug='test-link', description='Тестовое описание группы')


@pytest.fixture
def post_with_group(user, group):
    image = tempfile.NamedTemporaryFile(suffix=".jpg").name
    return Post.objects.create(text='Тестовый пост 2', author=user, group=group, image=image)


@pytest.fixture
def few_posts_with_group(mixer, user, group):
    """Return one record with the same author and group."""
    posts = mixer.cycle(20).blend(Post, author=user, group=group)
    return posts[0]


@pytest.fixture
def another_few_posts_with_group_with_follower(mixer, user, another_user, group):
    mixer.blend('posts.Follow', user=user, author=another_user)
    mixer.cycle(20).blend(Post, author=another_user, group=group)


@pytest.fixture
def group_1():
    from posts.models import Group
    return Group.objects.create(title='Группа 1', slug='group_1')


@pytest.fixture
def group_2():
    from posts.models import Group
    return Group.objects.create(title='Группа 2', slug='group_2')


@pytest.fixture
def post_1(user, group_1):
    from posts.models import Post
    return Post.objects.create(text='Тестовый пост 1', author=user, group=group_1)


@pytest.fixture
def post_2(user, group_1):
    from posts.models import Post
    return Post.objects.create(text='Тестовый пост 12342341', author=user, group=group_1)


@pytest.fixture
def comment_1_post(post_1, user):
    from posts.models import Comment
    return Comment.objects.create(author=user, post=post_1, text='Коммент 1')


@pytest.fixture
def comment_2_post(post_1, another_user_2):
    from posts.models import Comment
    return Comment.objects.create(author=another_user_2, post=post_1, text='Коммент 2')


@pytest.fixture
def another_post(another_user_2, group_2):
    from posts.models import Post
    return Post.objects.create(text='Тестовый пост 2', author=another_user_2, group=group_2)


@pytest.fixture
def comment_1_another_post(another_post, user):
    from posts.models import Comment
    return Comment.objects.create(author=user, post=another_post, text='Коммент 12')


@pytest.fixture
def follow_1(user, another_user_2):
    from posts.models import Follow
    return Follow.objects.create(user=user, author=another_user_2)


@pytest.fixture
def follow_2(user_2, user):
    from posts.models import Follow
    return Follow.objects.create(user=user_2, author=user)


@pytest.fixture
def follow_3(user_2, another_user_2):
    from posts.models import Follow
    return Follow.objects.create(user=user_2, author=another_user_2)


@pytest.fixture
def follow_4(another_user_2, user):
    from posts.models import Follow
    return Follow.objects.create(user=another_user_2, author=user)


@pytest.fixture
def follow_5(user_2, user):
    from posts.models import Follow
    return Follow.objects.create(user=user, author=user_2)
