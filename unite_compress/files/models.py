from django.conf import settings
from django.db import models
from django.utils import timezone

from unite_compress.files.utils import file_generate_upload_path


class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class File(BaseModel):
    file = models.FileField(upload_to=file_generate_upload_path, blank=True, null=True)

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

    @property
    def is_valid(self):
        """
        We consider a file "valid" if the the datetime flag has value.
        """
        return bool(self.upload_finished_at)

    @property
    def url(self):
        # if "S3" in settings.DEFAULT_FILE_STORAGE:
        #     return self.file.url

        # return f"{settings.ALLOWED_HOSTS[0]}/{self.file.url}"
        return self.file.url
