from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTests(TestCase):
    def setUp(self):
        AboutViewsTests.guest_client = Client()

    def test_urls_use_correct_template(self):
        """URL-адреса доступны и используют соответствующий шаблон."""
        templates_pages_names = {
            'author.html': reverse('about:author'),
            'tech.html': reverse('about:tech'),
        }
        for template, path in templates_pages_names.items():
            with self.subTest(path=path):
                response = AboutViewsTests.guest_client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, template)
