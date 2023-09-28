from django.http import HttpResponseBadRequest
from rest_framework import (
    status,
    generics,
)

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import views

from config import settings
from processing.models import File
from processing.serializers import FileSerializer
from processing.services import FileProcessService
from processing.tasks import process_uploaded_file


class FileProcessingApiView(views.APIView):
    permission_classes = (IsAuthenticated,)

    serializer_class = FileSerializer

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('file')
        # TODO: предусмотреть загрузку нескольких файлов в запросе

        if not uploaded_file:
            return HttpResponseBadRequest('File not provided.')

        if uploaded_file.size >= settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            return HttpResponseBadRequest(
                'File is too big ({} > {})'.format(
                    uploaded_file.size, settings.FILE_UPLOAD_MAX_MEMORY_SIZE
                )
            )
        file_instance = FileProcessService.create(
            file=uploaded_file,
            uploaded_by=self.request.user,
        )

        process_uploaded_file.delay(file_instance.pk)

        serializer = self.serializer_class(file_instance)
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED,
        )


class FileListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = File.objects.all()
    serializer_class = FileSerializer
    http_method_names = ["get"]
