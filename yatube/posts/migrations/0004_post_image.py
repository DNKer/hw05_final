# Generated by Django 2.2.16 on 2022-11-21 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20221121_1915'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Загрузите сюда вашу картинку', upload_to='posts/', verbose_name='Картинка'),
        ),
    ]
