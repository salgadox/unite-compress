from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from unite_compress.files.api.serializers import AsyncResultSerializer, FileSerializer
from unite_compress.files.client import s3_generate_presigned_get
from unite_compress.files.mixins import ApiAuthMixin
from unite_compress.files.models import File
from unite_compress.files.services import (
    FileDirectUploadService,
    FileStandardUploadService,
)
from unite_compress.files.tasks import convert_file
from unite_compress.files.utils import Converter, convert_path


class FileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    # mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    queryset = File.objects.all()
    serializer_class = FileSerializer

    def get_queryset(self):
        return self.queryset.filter(uploaded_by=self.request.user)

    @action(
        detail=True,
        methods=["GET"],
    )
    def generate_url(self, request, pk):
        file = self.queryset.get(pk=pk)
        # TODO Fix: Hardecoded media
        if "S3" in settings.DEFAULT_FILE_STORAGE:
            file_path = convert_path("media/" + file.file.name)
            url = s3_generate_presigned_get(file_path=file_path)
        else:
            url = file.url

        return Response({"url": url}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"])
    def tasks(self, request, pk):
        # Check if there are any existing tasks for the new model instance
        existing_tasks = convert_file.AsyncResult(str(pk))
        serializer = AsyncResultSerializer(existing_tasks)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def convert(self, request, pk):
        file = self.queryset.get(pk=pk)
        # Check if there are any existing tasks for the new model instance
        if file.convert_status == "pending":
            # If no task exists, create a new task and return it
            try:
                command_id = Converter.choose_convert_command(file).id
            except AttributeError:
                message = "cannot convert: file type not supported"
                _status = status.HTTP_400_BAD_REQUEST
            else:
                task = convert_file.delay(command_id, pk)
                serializer = AsyncResultSerializer(task)
                return Response(
                    {"task": serializer.data, "message": "Task created"},
                    status=status.HTTP_201_CREATED,
                )
        else:
            if file.convert_status == "started":
                # Task exists, return message and status
                message = "File conversion in progress"
                _status = status.HTTP_204_NO_CONTENT
            if file.convert_status == "converted":
                # File has been converted, return message and status
                message = "File has been converted"
                _status = status.HTTP_204_NO_CONTENT
            else:
                message = "File conversion error"
                _status = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(
            {"message": message},
            status=_status,
        )


class FileStandardUploadApi(ApiAuthMixin, APIView):
    def post(self, request):
        service = FileStandardUploadService(
            user=request.user, file_obj=request.FILES["file"]
        )
        file = service.create()

        return Response(data={"id": file.id}, status=status.HTTP_201_CREATED)


class FileDirectUploadStartApi(ApiAuthMixin, APIView):
    class InputSerializer(serializers.Serializer):
        file_name = serializers.CharField()
        file_type = serializers.CharField()

    def post(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = FileDirectUploadService(request.user)
        presigned_data = service.start(**serializer.validated_data)

        return Response(data=presigned_data)


class FileDirectUploadLocalApi(ApiAuthMixin, APIView):
    def post(self, request, file_id):
        file = get_object_or_404(File, id=file_id)

        file_obj = request.FILES["file"]

        service = FileDirectUploadService(request.user)
        file = service.upload_local(file=file, file_obj=file_obj)

        return Response({"id": file.id})


class FileDirectUploadFinishApi(ApiAuthMixin, APIView):
    class InputSerializer(serializers.Serializer):
        file_id = serializers.CharField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_id = serializer.validated_data["file_id"]

        file = get_object_or_404(File, id=file_id)

        service = FileDirectUploadService(request.user)
        service.finish(file=file)

        return Response({"id": file.id})
