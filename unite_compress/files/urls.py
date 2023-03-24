from django.urls import path

from unite_compress.files.views import (
    FileDetailView,
    FileListView,
    FileUploadView,
    file_converting_view,
    latest_file_view,
)

app_name = "files"
urlpatterns = [
    path("", FileListView.as_view(), name="list"),
    path("upload/", FileUploadView.as_view(), name="upload"),
    path("<str:file_name>/", FileDetailView.as_view(), name="detail"),
    path("latest-file", latest_file_view, name="latest-file"),
    path("file-converting", file_converting_view, name="file-converting"),
]
