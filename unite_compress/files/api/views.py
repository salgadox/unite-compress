from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from unite_compress.files.api.serializers import FileSerializer
from unite_compress.files.client import s3_generate_presigned_get
from unite_compress.files.mixins import ApiAuthMixin
from unite_compress.files.models import File
from unite_compress.files.services import (
    FileDirectUploadService,
    FileStandardUploadService,
)


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
            url = s3_generate_presigned_get(file_path="media/" + file.file.name)
        else:
            url = file.url

        return Response({"url": url}, status=status.HTTP_200_OK)


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
