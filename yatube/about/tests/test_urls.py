from django.test import Client, TestCase


class AboutURLTests(TestCase):
    def setUp(self):
        AboutURLTests.guest_client = Client()

    def test_urls_exists_at_desired_location(self):
        """Проверка доступности адресов приложения about."""
        path_list = [
            '/about/author/',
            '/about/tech/',
        ]
        for path in path_list:
            with self.subTest(path=path):
                response = AboutURLTests.guest_client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """Проверка шаблонов для адресов приложения about."""
        templates_url_names = {
            'author.html': '/about/author/',
            'tech.html': '/about/tech/',
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = AboutURLTests.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
