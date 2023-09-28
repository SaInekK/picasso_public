from django.urls import path

from processing.views import (
    FileProcessingApiView,
    FileListView,
)

urlpatterns = [
    path('files/', FileListView.as_view(), name='files-list'),
    path('upload/', FileProcessingApiView.as_view(), name='files-post'),
]
