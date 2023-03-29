from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Course(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("name"))
    description = models.TextField(blank=True, verbose_name=_("description"))
    created_at = models.DateTimeField(db_index=True, default=timezone.now)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
