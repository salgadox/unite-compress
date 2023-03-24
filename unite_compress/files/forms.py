from dal import autocomplete

from unite_compress.files.models import File
from unite_compress.files.widgets import DragAndDropFileInput


class FileForm(autocomplete.FutureModelForm):
    class Meta:
        model = File
        fields = ["file", "course"]
        widgets = {
            "file": DragAndDropFileInput(),
            "course": autocomplete.ModelSelect2(
                url="courses:autocomplete", attrs={"data-minimum-input-length": 0}
            ),
        }
