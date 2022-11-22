import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    """Создаем тестовые посты и группы."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.user = User.objects.create_user(username='leo')
        cls.another_user = User.objects.create_user(username='dnk')
        cls.group = Group.objects.create(
            title='Тестовая Группа',
            slug='prosaics',
            description='тестовое описание группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=(
                'Грусть моя, как пленная сербка, '
                'Родной произносит свой толк. '
                'Напевному слову так терпко '
                'В устах, целовавших твой шелк.'
            ),
            group=cls.group,
            image=uploaded,
        )
        cls.comment_post = Comment.objects.create(
            author=cls.user,
            text='Мой комментарий на все четыре тома.',
            post=cls.post
        )

    @classmethod
    def tearDownClass(cls):
        """Удаляем тестовые медиа."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создаем клиент зарегистрированного пользователя."""
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewTests.user)
        cache.clear()

    def test_paginator_correct_context(self):
        """Шаблоны index, group_list и profile отображаются правильно"""
        paginator_objects = []
        for i in range(1, 18):
            new_post = Post(
                author=PostViewTests.user,
                text=f'Тестовый пост {i}',
                group=PostViewTests.group
            )
            paginator_objects.append(new_post)
        Post.objects.bulk_create(paginator_objects)
        paginator_data = {
            'index': reverse('posts:index'),
            'group': reverse(
                'posts:group_list',
                kwargs={'slug': PostViewTests.group.slug}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': PostViewTests.user.username}
            )
        }
        for paginator_place, paginator_page in paginator_data.items():
            with self.subTest(paginator_place=paginator_place):
                response_page_1 = self.authorized_client.get(paginator_page)
                response_page_2 = self.authorized_client.get(
                    paginator_page + '?page=2'
                )
                self.assertEqual(len(
                    response_page_1.context['page_obj']), 10
                )
                self.assertEqual(len(
                    response_page_2.context['page_obj']), 8
                )

    def test_posts_index_cache(self):
        """Кэш на главной странице работает правильно."""
        cache.clear()
        response1 = self.authorized_client.get(reverse('posts:index'))
        Post.objects.create(
            author=self.user,
            text=self.post.text,
        )
        response2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response1.content, response2.content)
        cache.clear()
        response3 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response1.content, response3.content)

    def test_group_list_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response_group_list = self.authorized_client.get(
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug})
        )
        task_post = response_group_list.context['page_obj'][0]
        task_group = response_group_list.context['group']
        self.assertEqual(task_post, self.post)
        self.assertEqual(task_group, self.group)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response_post_detail = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            )
        )
        response_post = response_post_detail.context['post']
        self.assertEqual(response_post, self.post)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.post.author})
        )
        post = response.context['page_obj'][0]
        self.assertEqual(post, self.post)
        self.assertEqual(response.context['author'], self.post.author)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
                self.assertIsInstance(response.context['form'], PostForm)
                self.assertIsNone(response.context.get('is_edit', None))

    def test_post_edit_page_show_correct_context(self):
        """Шаблон create_post(edit) сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostViewTests.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
                self.assertIsInstance(response.context['form'], PostForm)
                self.assertTrue(response.context['is_edit'])
                self.assertIsInstance(response.context['is_edit'], bool)

    def test_follow(self):
        """Тестирование подписки на автора."""
        count_follow = Follow.objects.count()
        new_author = User.objects.create(username='neo_leo')
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': new_author.username}
            )
        )
        follow = Follow.objects.last()
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        self.assertEqual(follow.author, new_author)
        self.assertEqual(follow.user, PostViewTests.user)

    def test_unfollow(self):
        """Тестирование отписки от автора."""
        count_follow = Follow.objects.count()
        new_author = User.objects.create(username='neo_leo')
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': new_author.username}
            )
        )
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': new_author.username}
            )
        )
        self.assertEqual(Follow.objects.count(), count_follow)

    def test_guest_client_cant_create_comment(self):
        """Неавторизированный пользователь не может создавать комментарий"""
        self.guest_client = Client()
        comment_count = Comment.objects.count()
        post_id = self.post.pk
        form_data = {
            'text': 'Комментарий некомментируемого события',
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post_id}),
            data=form_data
        )
        self.assertEqual(Comment.objects.count(), comment_count,
                         'Ошибка. Guest_client может создавать comment.')

    def test_post_in_line_subscriber(self):
        """
        Новая запись пользователя появляется в ленте тех, кто на него подписан
        """
        response = self.authorized_client.get(reverse('posts:follow_index'))
        count_before_follow = len(response.context.get('page_obj'))
        Follow.objects.get_or_create(user=self.user, author=self.user)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        count_after_follow = len(response.context.get('page_obj'))
        self.assertEqual(count_before_follow + 1, count_after_follow,
                         'Ошибка. Count_before + 1 != Count_after. '
                         'Нет новой записи у подписчика.')
        cache.clear()

    def test_post_in_line_isnt_subscriber(self):
        """
        Новая запись пользователя не появляется в ленте тех,
        кто не подписан
        """
        self.authorized_client.force_login(self.another_user)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        count_posts_in_unfollow_user = len(response.context.get('page_obj'))
        self.assertEqual(count_posts_in_unfollow_user, 0,
                         'Ошибка. Count_posts NOT NULL! '
                         'Появляется запись у неявляющегося подписчиком.')
        cache.clear()

    def test_pages_show_correct_image(self):
        """Проверяем, что передан объект класса image"""
        templates_pages_names = {
            reverse('posts:index'),
            reverse(
                'posts:group_list', kwargs={'slug': PostViewTests.group.slug}
            ),
            reverse(
                'posts:profile', kwargs={'username': PostViewTests.user}
            ),
        }
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                image_field = response.context['page_obj'][0].image.name
                image_name = 'posts/small.gif'
                self.assertEqual(image_field, image_name)

        reverse_name = reverse(
            'posts:post_detail',
            kwargs={'post_id': PostViewTests.post.pk},
        )
        response = self.authorized_client.get(reverse_name)
        image_field = response.context['post'].image.name
        image_name = 'posts/small.gif'
        self.assertEqual(image_field, image_name)
