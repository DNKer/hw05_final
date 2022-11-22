from django.contrib.auth import get_user_model
from django.db import models

TEXT_LIMIT_POST: int = 15
TEXT_LIMIT_COMMENT: int = 30

User = get_user_model()


class Group(models.Model):
    title = models.fields.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    slug = models.fields.SlugField(
        max_length=255,
        unique=True,
        verbose_name='Заголовок'
    )
    description = models.fields.TextField(
        max_length=255,
        verbose_name='Описание'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Введите текст публикации'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )

    group = models.ForeignKey(
        Group,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой относится публикация'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Загрузите сюда вашу картинку'
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:TEXT_LIMIT_POST]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='comments',
        verbose_name='Комментарии'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор публикации'
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Напишите комментарий',
    )
    created = models.DateTimeField(
        'Дата комментария',
        auto_now_add=True,
    )

    def __str__(self):
        return self.text[:TEXT_LIMIT_COMMENT]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'], name='follow')
        ]
