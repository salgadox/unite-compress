from django import forms

from unite_compress.files.models import File


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ["file"]
