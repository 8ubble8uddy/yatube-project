import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

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
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='username')
        cls.group = Group.objects.create(
            title='Группа', slug='slug', description='Описание группы'
        )
        cls.post = Post.objects.create(
            text='текст', author=cls.user, group=cls.group, image=None
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def is_post_correct(self, form_data, expected):
        """Проверяет на соответствие словаря form_data с expected."""
        text = form_data['text']
        group = form_data['group']
        image = form_data['image']
        self.assertEqual(text, expected.text)
        self.assertEqual(self.user, expected.author)
        self.assertEqual(group, expected.group.id if expected.group else '')
        self.assertEqual(image.name, expected.image.name.split('/')[1])

    def test_new_post_creates_post(self):
        """Валидная форма создает запись в Post."""
        path = reverse('new_post')
        uploaded = SimpleUploadedFile(
            name='small_1.gif',
            content=GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'новый текст',
            'group': self.group.id,
            'image': uploaded,
        }
        posts_count = Post.objects.count()
        response = self.authorized_client.post(path, form_data, follow=True)
        redirect = reverse('index')
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        expected = Post.objects.first()
        self.is_post_correct(form_data, expected)

    def test_new_post_cant_create_empty_post(self):
        """Форма не позволяет создать пустую запись."""
        path = reverse('new_post')
        form_data = {
            'text': '',
            'group': self.group.id,
            'image': '',
        }
        posts_count = Post.objects.count()
        response = self.authorized_client.post(path, form_data, follow=True)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFormError(response, 'form', 'text', 'Обязательное поле.')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_changes_post(self):
        """При редактировании поста изменяется соответствующий пост."""
        kwargs_post = {
            'username': self.post.author.username,
            'post_id': self.post.id,
        }
        path = reverse('post_edit', kwargs=kwargs_post)
        uploaded = SimpleUploadedFile(
            name='small_2.gif',
            content=GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'новый текст',
            'group': '',
            'image': uploaded,
        }
        posts_count = Post.objects.count()
        response = self.authorized_client.post(path, form_data, follow=True)
        self.post.refresh_from_db()
        redirect = reverse('post_view', kwargs=kwargs_post)
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count)
        expected = self.post
        self.is_post_correct(form_data, expected)

    def test_add_comment_create_comment(self):
        """Валидная форма создает комментарий в Comment."""
        kwargs_post = {
            'username': self.post.author.username,
            'post_id': self.post.id,
        }
        path = reverse('add_comment', kwargs=kwargs_post)
        form_data = {
            'text': 'новый комментарий',
        }
        comments_count = Comment.objects.count()
        response = self.authorized_client.post(path, form_data, follow=True)
        redirect = reverse('post_view', kwargs=kwargs_post)
        self.assertRedirects(response, redirect)
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        new_comment = Comment.objects.first()
        text = form_data['text']
        post_id = kwargs_post['post_id']
        author = self.user
        self.assertEqual(text, new_comment.text)
        self.assertEqual(post_id, new_comment.post.id)
        self.assertEqual(author, new_comment.author)
