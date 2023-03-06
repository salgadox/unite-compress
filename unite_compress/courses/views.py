from dal import autocomplete
from django.db.models import Count
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from unite_compress.courses.models import Course


class CourseAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Course.objects.filter(created_by=self.request.user)
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs


class CourseListView(ListView):
    model = Course
    template_name = "course_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        return Course.objects.filter(created_by=self.request.user).annotate(
            file_count=Count("files")
        )


class CourseDetailView(DetailView):
    model = Course
    template_name = "courses/course_detail.html"
    context_object_name = "course"
    slug_url_kwarg = "course_slug"
    slug_field = "slug"


class CourseCreateView(CreateView):
    model = Course
    fields = ["name", "description"]
    template_name = "courses/course_create.html"
    success_url = reverse_lazy("courses:list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class CourseDeleteView(DeleteView):
    model = Course
    template_name = "courses/course_delete.html"
    success_url = reverse_lazy("courses:list")
    slug_url_kwarg = "course_slug"
    slug_field = "slug"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.created_by == self.request.user:
            raise Http404
        return obj
