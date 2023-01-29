from rest_framework import serializers

from unite_compress.files.models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
            "file_name",
            "file_type",
            "created_at",
            "url",
        ]
