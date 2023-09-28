from django.contrib.auth import get_user_model
from django.db import models


class File(models.Model):
    file = models.FileField(
        verbose_name='Загруженный файл',
        blank=True,
        null=True,
    )
    cdn_url = models.CharField(
        verbose_name='CDN URL',
        blank=True,
        null=True,
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата/время загрузки',
    )
    file_type = models.CharField(
        verbose_name='Тип файла',
        blank=True,
        null=True,
    )
    uploaded_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Юзер, загрузивший файл',
    )
    processed = models.BooleanField(
        default=False,
        verbose_name='Обработан ли файл',
    )
