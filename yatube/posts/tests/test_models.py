from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()

FIRST_CHAR_NUMBER: int = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=(
                'Грусть моя, как пленная сербка, '
                'Родной произносит свой толк. '
                'Напевному слову так терпко '
                'В устах, целовавших твой шелк.'
            )
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        self.assertEqual(str(post), post.text[:FIRST_CHAR_NUMBER])

    def test_grope_have_correct_grop_title(self):
        """Проверяем, что у группы корректно работает title."""
        group = PostModelTest.group
        self.assertEqual(str(group), group.title)

    def test_models_have_verbose_name(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_models_have_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст публикации',
            'group': 'Группа, к которой относится публикация'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
