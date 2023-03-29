from botocore.exceptions import ClientError
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from unite_compress.courses.models import Course
from unite_compress.files.client import s3_get_file_size
from unite_compress.files.utils import convert_path, file_generate_upload_path


class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


CONVERSION_STATUS_CHOICES = (
    ("pending", _("Convert pending")),
    ("started", _("Convert started")),
    ("converted", _("Converted")),
    ("error", _("Not converted due to error")),
)

COMPRESSION_RATES = (
    ("low", _("Low compression rate")),
    ("medium", _("Medium compression rate")),
    ("high", _("High compression rate")),
)


class File(BaseModel):
    file = models.FileField(
        upload_to=file_generate_upload_path,
        blank=True,
        null=True,
        verbose_name=_("File"),
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="files",
        blank=True,
        null=True,
        verbose_name=_("Folder"),
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
        verbose_name=_("Conversion status"),
        choices=CONVERSION_STATUS_CHOICES,
        default="pending",
    )
    converted_at = models.DateTimeField(
        verbose_name=_("Convert time"),
        editable=False,
        null=True,
        blank=True,
    )
    last_convert_msg = models.TextField(
        verbose_name=_("Message from last converting command"), blank=True, default=""
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
    def original_file_size(self):
        try:
            file_size = self.file.size
        except ClientError:
            file_size = 0
        return file_size

    @property
    def converted_file_size(self):
        try:
            file_size = s3_get_file_size(
                file_path=convert_path("media/" + self.file.name)
            )
        except ClientError:
            file_size = 0
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
        verbose_name=_("Title"),
        null=True,
        blank=True,
    )
    mime_regex = models.CharField(
        max_length=255,
        verbose_name=_("Regex to match mime types"),
    )
    is_enabled = models.BooleanField(
        verbose_name=_("Enabled?"),
        default=True,
    )
    command = models.TextField(
        verbose_name=_("System command to convert video"),
    )

    compression_rate = models.CharField(
        max_length=16,
        verbose_name=_("compression rate"),
        choices=COMPRESSION_RATES,
        default="medium",
    )
