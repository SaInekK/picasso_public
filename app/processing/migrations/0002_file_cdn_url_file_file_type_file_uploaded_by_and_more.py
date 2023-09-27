# Generated by Django 4.2.5 on 2023-09-26 21:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('processing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='cdn_url',
            field=models.CharField(blank=True, null=True, verbose_name='CDN URL'),
        ),
        migrations.AddField(
            model_name='file',
            name='file_type',
            field=models.CharField(blank=True, null=True, verbose_name='Тип файла'),
        ),
        migrations.AddField(
            model_name='file',
            name='uploaded_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Юзер, загрузивший файл'),
        ),
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='Загруженный файл'),
        ),
    ]