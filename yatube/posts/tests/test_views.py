import shutil
import tempfile
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User

MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='username')
        cls.group = Group.objects.create(
            title='Группа', slug='slug', description='Описание группы'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=GIF,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='текст', author=cls.user, group=cls.group, image=uploaded
        )
        cls.comment = Comment.objects.create(
            text='комментарий', post=cls.post, author=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def is_post_correct(self, post, expected):
        """Проверяет на соответствие значение полей post с expected."""
        self.assertEqual(post.text, expected.text)
        self.assertEqual(post.pub_date, expected.pub_date)
        self.assertEqual(post.author, expected.author)
        self.assertEqual(post.group, expected.group)
        if post.image:
            self.assertEqual(post.image, expected.image)

    def is_form_instance(self, form):
        """Проверяет на соответствие полей form с указанным классом"""
        text_field = form.fields['text']
        group_field = form.fields['group']
        image_field = form.fields['image']
        self.assertIsInstance(text_field, forms.fields.CharField)
        self.assertIsInstance(group_field, forms.fields.ChoiceField)
        self.assertIsInstance(image_field, forms.fields.ImageField)

    def is_form_correct(self, form, expected):
        """Проверяет на соответствие значение полей form с expected."""
        text = form['text'].value() or ''
        group = form['group'].value()
        image = form['image'].value()
        self.assertEqual(text, expected.text)
        self.assertEqual(group, expected.group.id if expected.group else None)
        if image:
            self.assertEqual(image, expected.image)

    def test_pages_use_correct_template(self):
        """URL-адреса доступны и используют соответствующий шаблон."""
        kwargs_group = {'slug': self.group.slug}
        templates_pages_names = {
            'index.html': reverse('index'),
            'postform.html': reverse('new_post'),
            'group.html': reverse('group_posts', kwargs=kwargs_group),
        }
        for template, path in templates_pages_names.items():
            with self.subTest(path=path):
                response = self.authorized_client.get(path)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_home_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        path = reverse('index')
        response = self.authorized_client.get(path)
        post = response.context['page'][0]
        expected = self.post
        self.is_post_correct(post, expected)

    def test_group_page_shows_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        kwargs_group = {'slug': self.group.slug}
        path = reverse('group_posts', kwargs=kwargs_group)
        response = self.authorized_client.get(path)
        group = response.context['group']
        expected_group = self.group
        self.assertEqual(group.title, expected_group.title)
        self.assertEqual(group.slug, expected_group.slug)
        self.assertEqual(group.description, expected_group.description)
        post = response.context['page'][0]
        expected = self.post
        self.is_post_correct(post, expected)

    def test_profile_page_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        kwargs_profile = {'username': self.user.username}
        path = reverse('profile', kwargs=kwargs_profile)
        response = self.authorized_client.get(path)
        author = response.context['author']
        expected_author = self.user
        self.assertEqual(author.username, expected_author.username)
        self.assertEqual(author.first_name, expected_author.first_name)
        self.assertEqual(author.last_name, expected_author.last_name)
        post = response.context['page'][0]
        expected = self.post
        self.is_post_correct(post, expected)

    def test_post_view_page_shows_correct_context(self):
        """Шаблон post_view сформирован с правильным контекстом."""
        kwargs_post = {
            'username': self.post.author.username,
            'post_id': self.post.id,
        }
        path = reverse('post_view', kwargs=kwargs_post)
        response = self.authorized_client.get(path)
        post = response.context['post']
        expected = self.post
        self.is_post_correct(post, expected)
        comment = response.context['comments'][0]
        expected_comment = self.comment
        self.assertEqual(comment.text, expected_comment.text)
        self.assertEqual(comment.created, expected_comment.created)
        self.assertEqual(comment.post, expected_comment.post)
        self.assertEqual(comment.author, expected_comment.author)

    def test_post_edit_page_shows_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        kwargs_post = {
            'username': self.post.author.username,
            'post_id': self.post.id,
        }
        path = reverse('post_edit', kwargs=kwargs_post)
        response = self.authorized_client.get(path)
        form = response.context['form']
        expected = self.post
        self.is_form_instance(form)
        self.is_form_correct(form, expected)

    def test_new_post_page_shows_correct_context(self):
        """Шаблон new_post сформирован с правильными контекстом."""
        path = reverse('new_post')
        response = self.authorized_client.get(path)
        form = response.context['form']
        expected = Post(None)
        self.is_form_instance(form)
        self.is_form_correct(form, expected)

    def test_group_post_doesnt_apear_in_another_group(self):
        """Пост группы не появляется в другой группе."""
        another_group = Group.objects.create(
            title='Другая группа', slug='slug_2', description='Описание группы'
        )
        kwargs_group = {'slug': another_group.slug}
        path = reverse('group_posts', kwargs=kwargs_group)
        response = self.authorized_client.get(path)
        group = response.context['group']
        post_list = response.context['page'].object_list
        expected_post = self.post
        self.assertNotEqual(group, expected_post.group)
        self.assertNotIn(expected_post, post_list)

    def test_cache_home_page(self):
        """Проверяет работу кэша на главной странице."""
        expected = Post.objects.create(text='кэш', author=self.user)
        path = reverse('index')
        response_1 = self.authorized_client.get(path)
        page = response_1.context['page']
        paginator = page.paginator
        self.assertEqual(paginator.num_pages, 1)
        expected.delete()
        response_2 = self.authorized_client.get(path)
        self.assertEqual(response_2.content, response_1.content)
        cache.clear()
        response_3 = self.authorized_client.get(path)
        self.assertNotEqual(response_3.content, response_1.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='username')
        cls.group = Group.objects.create(
            title='Группа', slug='slug', description='Описание группы'
        )
        for count in range(15):
            Post.objects.create(text='текст', author=cls.user, group=cls.group)

    def setUp(self):
        self.guest_client = Client()

    def test_paginator_shows_correct_amount_of_posts(self):
        """Проверка паджинатора: передаётся по 10 записей на страницу."""
        kwargs_group = {'slug': self.group.slug}
        kwargs_profile = {'username': self.user.username}
        path_list = [
            reverse('index'),
            reverse('group_posts', kwargs=kwargs_group),
            reverse('profile', kwargs=kwargs_profile),
        ]
        for path in path_list:
            with self.subTest(path=path):
                # Проверяем количество постов на первой странице (10 постов)
                response = self.guest_client.get(path)
                page_1 = response.context.get('page')
                self.assertEqual(len(page_1.object_list), 10)
                # Проверяем количество постов на второй странице (5 постов)
                response = self.guest_client.get(path + '?page=2')
                page_2 = response.context.get('page')
                self.assertEqual(len(page_2.object_list), 5)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create(username='follower')
        cls.following = User.objects.create(username='following')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.follower)

    def test_profile_follow_by_follower(self):
        """Авторизованный пользователь может подписаться на пользователя."""
        kwargs_profile = {'username': self.following.username}
        path = reverse('profile_follow', kwargs=kwargs_profile)
        follow_count = Follow.objects.count()
        self.authorized_client.get(path, follow=True)
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.follower, author=self.following
            ).exists()
        )

    def test_profile_unfollow_by_follower(self):
        """Авторизованный пользователь может отписаться от пользователя."""
        Follow.objects.create(user=self.follower, author=self.following)
        kwargs_profile = {'username': self.following.username}
        path = reverse('profile_unfollow', kwargs=kwargs_profile)
        follow_count = Follow.objects.count()
        self.authorized_client.get(path, follow=True)
        self.assertEqual(Follow.objects.count(), follow_count - 1)
        self.assertFalse(
            Follow.objects.filter(
                user=self.follower, author=self.following
            ).exists()
        )

    def test_follow_index_shows_correct_post(self):
        """При подписке в ленте подписок появляются новые посты автора."""
        Follow.objects.create(user=self.follower, author=self.following)
        expected = Post.objects.create(text='подписка', author=self.following)
        path = reverse('follow_index')
        response = self.authorized_client.get(path)
        post_list = response.context['page'].object_list
        self.assertIn(expected, post_list)

    def test_new_post_doesnt_appear_on_unfollow_index(self):
        """При отписке в ленте подписок не появляются новые посты автора."""
        expected = Post.objects.create(text='отписка', author=self.following)
        path = reverse('follow_index')
        response = self.authorized_client.get(path)
        post_list = response.context['page'].object_list
        self.assertNotIn(expected, post_list)
