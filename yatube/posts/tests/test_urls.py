from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='username')
        cls.group = Group.objects.create(
            title='Группа', slug='slug', description='Описание группы'
        )
        cls.post = Post.objects.create(
            text='текст', author=cls.user, group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_available_for_anonymous_at_desired_location(self):
        """Проверка доступности адресов для анонимного пользователя."""
        path_list = [
            '/',
            f'/group/{self.group.slug}/',
            f'/{self.user.username}/',
            f'/{self.user.username}/{self.post.id}/',
        ]
        for path in path_list:
            with self.subTest(path=path):
                response = self.guest_client.get(path)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_available_and_redirect_anonymous_on_admin_login(self):
        """Проверка доступa и перенаправления анонимного пользователя."""
        path_list = [
            '/new/',
            f'/{self.user.username}/{self.post.id}/edit/',
            f'/{self.user.username}/{self.post.id}/comment/',
        ]
        for path in path_list:
            with self.subTest(path=path):
                response = self.guest_client.get(path, follow=True)
                redirect = f'/auth/login/?next={path}'
                self.assertRedirects(response, redirect)

    def test_urls_use_correct_template(self):
        """Проверка шаблонов для адресов приложения posts."""
        templates_url_names = {
            '/': 'index.html',
            '/new/': 'postform.html',
            f'/group/{self.group.slug}/': 'group.html',
            f'/{self.user.username}/{self.post.id}/edit/': 'postform.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_post_edit_url_redirects_authorized_without_access(self):
        """Проверка перенаправления пользователя, не имеющий прав доступа."""
        user_2 = User.objects.create(username='username_2')
        self.authorized_client.force_login(user_2)
        path = f'/{self.user.username}/{self.post.id}/edit/'
        response = self.authorized_client.get(path, follow=True)
        redirect = f'/{self.user.username}/{self.post.id}/'
        self.assertRedirects(response, redirect)

    def test_404(self):
        path = '/jxvjnsvnnoitstr/kfdpckpfpede/'
        response = self.guest_client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'misc/404.html')
