from django.test import TestCase


class ViewTestClass(TestCase):
    def test_error_page(self):
        """Статус ответа 404 и используется шаблон 404.html"""
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
