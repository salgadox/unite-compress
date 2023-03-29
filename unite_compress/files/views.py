from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView

from unite_compress.courses.models import Course
from unite_compress.files.forms import FileForm
from unite_compress.files.models import File


class FileListView(ListView):
    model = File
    template_name = "files/file_list.html"
    context_object_name = "files"

    def get_queryset(self):
        return File.objects.filter(uploaded_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["courses"] = Course.objects.filter(created_by=self.request.user)
        return context


class FileDetailView(DetailView):
    model = File
    template_name = "files/file_detail.html"
    context_object_name = "file"
    slug_url_kwarg = "file_name"
    slug_field = "file_name"


def latest_file_view(request):
    latest_file = File.objects.filter(uploaded_by=request.user).last()
    messages.success(request, _("Your file has been uploaded successfully."))
    return render(request, "files/file_detail.html", {"file": latest_file})


def file_converting_view(request):
    messages.success(request, _("Your file is being converted."))
    return redirect("files:list")


class FileUploadView(FormView):
    template_name = "files/file_upload.html"
    form_class = FileForm
