import os
from typing import Optional

import boto3
import mimetypes

from PIL import Image
from PyPDF2 import PdfReader

from config import settings
from processing.models import File


class FileProcessException(Exception):
    pass


class FileProcessService:
    def __init__(self, file_id: int):
        self.file_id = file_id
        self.file_instance = self._get_file_instance()
        self.file_name = self.file_instance.file.name
        self.file_path = f'{settings.MEDIA_ROOT}/{self.file_name}'
        self.file_type = self._infer_mime_type(self.file_path)
        self.resource = self._get_s3_resource()
        self.bucket = self._get_s3_bucket()

    @staticmethod
    def _get_s3_resource():
        return boto3.resource(
            service_name='s3',
            endpoint_url=settings.S3_ENDPOINT_URL,
            region_name='ru-1',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    def _get_s3_bucket(self):
        return self.resource.Bucket(settings.S3_DEFAULT_BUCKET)

    def _get_file_instance(self):
        return File.objects.get(pk=self.file_id)

    def process_file(self):
        if not self.file_type:
            raise FileProcessException('Неизвестный тип файла')
        if self.file_type.startswith('image'):
            self.process_image()
            return
        if self.file_type.endswith('pdf'):
            self.process_pdf()
            return
        raise FileProcessException('Невозможно обработать файл')

    def process_image(self):
        self._compress_image()
        self._s3_upload()
        self._update_s3_uploaded_file_instance()

    def process_pdf(self):
        if not os.path.isfile(self.file_path):
            return
        text = self._extract_pdf_text()
        parsed_file_name = f'{self.file_name}_parsed.txt'
        with open(parsed_file_name, 'w') as f:
            f.write(text)

        self._s3_upload(filename=parsed_file_name)
        self._update_s3_uploaded_file_instance(filename=parsed_file_name)

    def _extract_pdf_text(self):
        reader = PdfReader(self.file_path)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
        return text

    def _compress_image(self,
                        resize_by: int = None,
                        quality: int = settings.FILE_COMPRESS_VALUE):
        image_obj = Image.open(self.file_path)

        if resize_by:
            resize_ratio = resize_by / 100
            width, height = image_obj.size
            resize_w = int(width * resize_ratio)
            resize_h = int(height * resize_ratio)
            image_obj = image_obj.resize((resize_w, resize_h), Image.LANCZOS)

        image_obj.save(self.file_path, optimize=True, quality=quality)

    def _s3_upload(self, filename: Optional[str] = None, delete_local_file=True):
        # TODO: Рассмотреть
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
        self.bucket.upload_file(
            Filename=filename or self.file_path,
            Key=os.path.basename(filename) if filename else self.file_name,
        )

        if delete_local_file:
            os.remove(self.file_path)
            self.file_instance.file = None

    def _update_s3_uploaded_file_instance(self,
                                          filename: Optional[str] = None):
        filename = filename or self.file_name
        self.file_instance.cdn_url = f'{settings.S3_CDN_URL}/{filename}'
        self.file_instance.processed = True
        self.file_instance.file_type = self.file_type
        self.file_instance.save()

    @staticmethod
    def _infer_mime_type(file_path: str = "") -> str:
        guessed_file_type, encoding = mimetypes.guess_type(file_path)
        if guessed_file_type is None:
            file_type = ""
        else:
            file_type = guessed_file_type

        return file_type

    @classmethod
    def create(cls,
               file: str,
               uploaded_by: settings.AUTH_USER_MODEL = None,
               ) -> File:
        obj = File(
            file=file,
            uploaded_by=uploaded_by,
        )

        obj.full_clean()
        obj.save()

        return obj
