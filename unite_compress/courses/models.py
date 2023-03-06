from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Course(models.Model):
    course_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(db_index=True, default=timezone.now)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.course_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.course_name
