import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    """Создаем тестовые посты, группу и форму."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')
        cls.group = Group.objects.create(
            title='Тестовая Группа',
            slug='prosaics',
            description='тестовое описание группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Вывожу тестовый пост',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        """Удаляем тестовые медиа."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def setUp(cls):
        """Создаем клиент зарегистрированного пользователя."""
        cls.authorized_client = Client()
        cls.authorized_client.force_login(PostFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Вывожу тестовый пост',
            'group': PostFormTests.group.pk,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': PostFormTests.user.username}
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post_ = PostFormTests.post
        objects_names = {
            post_.group: post.group,
            post_.author: post.author,
            post_.text: post.text,
            post_.image: post.image,
        }
        for object_, value in objects_names.items():
            with self.subTest(object_=object_):
                self.assertEqual(object_, value)

    def test_edit_post(self):
        """Форма редактирует запись в Post."""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Измененный старый пост',
            'group': PostFormTests.group.pk,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostFormTests.post.pk}
            ),
            data=form_data,
        )
        post = Post.objects.get(pk=PostFormTests.post.pk)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': PostFormTests.post.pk}
        ))
        objects_names = {
            post.text: form_data['text'],
            post.group.pk: form_data['group'],
        }
        for object_, value in objects_names.items():
            with self.subTest(object_=object_):
                self.assertEqual(object_, value)

    def test_create_comment(self):
        """После успешной отправки комментарий появляется на странице поста"""
        comment_count = Comment.objects.count()
        post_id = self.post.pk
        form_data = {
            'text': 'Ой там на горі ой там на крутій '
                    'Ой там сиділо пара голубів.',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post_id}),
            data=form_data
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post_id})
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Ой там на горі ой там на крутій '
                     'Ой там сиділо пара голубів.'
            ).exists(),
            'Комментарий не соответствует ожидаемому'
        )
