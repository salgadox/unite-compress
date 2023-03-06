from django.forms.widgets import ClearableFileInput


class DragAndDropFileInput(ClearableFileInput):
    template_name = "files/widgets/drag_and_drop_file_input.html"

    class Media:
        css = {"all": ("css/drag-and-drop.css",)}
        js = ("js/drag-and-drop.js",)
