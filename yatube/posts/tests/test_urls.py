from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.auth_user = User.objects.create_user(username='TestAuthUser')
        cls.group = Group.objects.create(
            title='Тестовая Группа',
            slug='dnk',
            description='тестовое описание группы'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
        )
        cls.form_comment_data = {
            'text': 'Новый комментарий',
        }

    def setUp(self):
        """Создаем клиент гостя, автора и зарегистрированного пользователя."""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.author)

    def test_urls_response_guest(self):
        """Проверяем статус страниц для гостя."""
        url_status = {
            reverse(
                'posts:group_list',
                kwargs={'slug': PostURLTests.group.slug}
            ): HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={'username': PostURLTests.auth_user.username}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostURLTests.post.pk}
            ): HTTPStatus.OK,
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostURLTests.post.pk}
            ): HTTPStatus.FOUND,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostURLTests.post.pk}
            ): HTTPStatus.FOUND,
            reverse('posts:post_create'): HTTPStatus.FOUND,
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostURLTests.auth_user.username}
            ): HTTPStatus.FOUND,
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostURLTests.auth_user.username}
            ): HTTPStatus.FOUND,
            reverse('posts:follow_index'): HTTPStatus.FOUND
        }
        for url, status_code in url_status.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_response_guest_redirect(self):
        """Проверяем редирект страниц для гостя."""
        url1 = '/auth/login/?next=/create/'
        url2 = f'/auth/login/?next=/posts/{self.post.pk}/edit/'
        pages = {'/create/': url1,
                 f'/posts/{self.post.id}/edit/': url2}
        for page, value in pages.items():
            response = self.guest_client.get(page)
            self.assertRedirects(response, value)

    def test_post_create_redirect_anonymous_on_login(self):
        """Страница 'posts/<int:post_id>/comment/' перенаправит
        анонимного пользователя на страницу логина.
        """
        response = PostURLTests.guest_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': PostURLTests.post.pk}
            ),
            data=PostURLTests.form_comment_data,
            follow=True
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{PostURLTests.post.pk}/comment/'
        )

    def test_pages_redirect(self):
        """Проверяем недоступность создания поста без авторизации."""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_error_404_page(self):
        """Проверяем запрос к несуществующей странице"""
        response = self.guest_client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
