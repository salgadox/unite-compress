from django.conf import settings
from django.db import models
from django.utils import timezone

from unite_compress.courses.models import Course
from unite_compress.files.client import s3_get_file_size
from unite_compress.files.utils import convert_path, file_generate_upload_path


class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


CONVERSION_STATUS_CHOICES = (
    ("pending", "Convert pending"),
    ("started", "Convert started"),
    ("converted", "Converted"),
    ("error", "Not converted due to error"),
)

COMPRESSION_RATES = (
    ("low", "Low compression rate"),
    ("medium", "Medium compression rate"),
    ("high", "High compression rate"),
)


class File(BaseModel):
    file = models.FileField(upload_to=file_generate_upload_path, blank=True, null=True)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="files", blank=True, null=True
    )
    original_file_name = models.TextField()

    file_name = models.CharField(max_length=255, unique=True)
    file_type = models.CharField(max_length=255)

    # As a specific behavior,
    # We might want to preserve files after the uploader has been deleted.
    # In case you want to delete the files too, use models.CASCADE & drop the null=True
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )

    upload_finished_at = models.DateTimeField(blank=True, null=True)

    # conversion attributes
    convert_status = models.CharField(
        max_length=16,
        verbose_name="Conversion status",
        choices=CONVERSION_STATUS_CHOICES,
        default="pending",
    )
    converted_at = models.DateTimeField(
        verbose_name="Convert time",
        editable=False,
        null=True,
        blank=True,
    )
    last_convert_msg = models.TextField(
        verbose_name="Message from last converting command", blank=True, default=""
    )

    @property
    def is_valid(self):
        """
        We consider a file "valid" if the the datetime flag has value.
        """
        return bool(self.upload_finished_at)

    @property
    def is_local(self):
        try:
            return self._is_local
        except AttributeError:
            try:
                _ = self.file.path
                self._is_local = True
            except NotImplementedError:
                self._is_local = False
            return self._is_local

    @property
    def filepath(self):
        if self.is_local:
            self._filepath = self.file.path
        else:
            self._filepath = self.file.storage.url(self.file.name)
        return self._filepath

    @property
    def converted_path(self):
        try:
            return self._converted_path
        except AttributeError:
            self._converted_path = convert_path(self.filepath)
            return self._converted_path

    @property
    def converted_file_size(self):
        file_size = s3_get_file_size("media/" + self.file.name)
        return file_size

    @property
    def url(self):
        # if "S3" in settings.DEFAULT_FILE_STORAGE:
        #     return self.file.url

        # return f"{settings.ALLOWED_HOSTS[0]}/{self.file.url}"
        return self.file.url


class ConvertingCommand(models.Model):
    """
    System commands for convertion videos to desired format
    """

    title = models.CharField(
        max_length=64,
        verbose_name="Title",
        null=True,
        blank=True,
    )
    mime_regex = models.CharField(
        max_length=255,
        verbose_name="Regex to match mime types",
    )
    is_enabled = models.BooleanField(
        verbose_name="Enabled?",
        default=True,
    )
    command = models.TextField(
        verbose_name="System command to convert video",
    )

    compression_rate = models.CharField(
        max_length=16,
        verbose_name="compression rate",
        choices=COMPRESSION_RATES,
        default="medium",
    )
