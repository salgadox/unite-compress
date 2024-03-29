from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from unite_compress.files.forms import FileForm
from unite_compress.files.models import ConvertingCommand, File
from unite_compress.files.services import FileStandardUploadService


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "original_file_name",
        "file_name",
        "file_type",
        "url",
        "uploaded_by",
        "created_at",
        "upload_finished_at",
        "is_valid",
    ]
    list_select_related = ["uploaded_by"]

    ordering = ["-created_at"]

    def get_form(self, request, obj=None, **kwargs):
        """
        That's a bit of a hack
        Dynamically change self.form, before delegating to the actual ModelAdmin.get_form
        Proper kwargs are form, fields, exclude, formfield_callback
        """
        if obj is None:
            self.form = FileForm

        return super().get_form(request, obj, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        """
        We want to show those fields only when we have an existing object.
        """

        if obj is not None:
            return [
                "original_file_name",
                "file_name",
                "file_type",
                "created_at",
                "updated_at",
                "upload_finished_at",
            ]

        return []

    def save_model(self, request, obj, form, change):
        try:
            cleaned_data = form.cleaned_data

            service = FileStandardUploadService(
                file_obj=cleaned_data["file"], user=request.user
            )

            if change:
                service.update(file=obj)
            else:
                service.create()
        except ValidationError as exc:
            self.message_user(request, str(exc), messages.ERROR)


@admin.register(ConvertingCommand)
class ConvertingCommandAdmin(admin.ModelAdmin):
    pass
