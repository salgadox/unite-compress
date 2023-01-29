from rest_framework import serializers

from unite_compress.files.models import File


# __unite-compression
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    remember_me = serializers.BooleanField(required=False)


# end


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
            "file_name",
            "file_type",
            "created_at",
            "url",
        ]


# unite_compression
class AsyncResultSerializer(serializers.Serializer):
    id = serializers.CharField()
    status = serializers.CharField()
    result = serializers.JSONField()

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "status": instance.status,
            "result": instance.result,
        }


# end
