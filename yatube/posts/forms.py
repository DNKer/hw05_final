from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)
        labels = {
            'text': _('Тело сообщения'),
            'group': _('Группа сообщения'),
            'image': _('Картинка к сообщению'),
        }
        help_texts = {
            'text': _('Введите сообщение'),
            'group': _('Укажите группу сообщения'),
            'image': _('Добавьте картинку'),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': _('Текст комментария'),
        }
