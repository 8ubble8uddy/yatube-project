from django.test import TestCase

from posts.models import Group, Post, User


class TestModelPost(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='текст' * 100,
            author=User.objects.create(username='username'),
        )

    def test_object_name_is_text_field(self):
        """__str__  post - это строчка с содержимым post.text."""
        post = TestModelPost.post
        object_name = str(post)
        excepted_object_name = post.text[:(len(object_name))]
        self.assertEqual(excepted_object_name, object_name)

    def test_object_name_max_length(self):
        """Метод str обрезает и не превышает пятнадцать символов поста."""
        post = TestModelPost.post
        length_object_name = len(str(post))
        is_right_max_length = length_object_name <= 15
        self.assertTrue(is_right_max_length)


class TestModelGroup(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа',
            slug='gruppa',
            description='Описание группы',
        )

    def test_object_name_is_title_field(self):
        """__str__  group - это строчка с содержимым group.title."""
        group = TestModelGroup.group
        object_name = str(group)
        excepted_object_name = group.title
        self.assertEqual(excepted_object_name, object_name)
