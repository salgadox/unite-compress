from django.urls import path

from unite_compress.courses.views import (
    CourseAutocomplete,
    CourseCreateView,
    CourseDeleteView,
    CourseDetailView,
    CourseListView,
)

app_name = "courses"
urlpatterns = [
    path("create/", CourseCreateView.as_view(), name="create"),
    path("", CourseListView.as_view(), name="list"),
    path("autocomplete/", CourseAutocomplete.as_view(), name="autocomplete"),
    path("<slug:course_slug>/", CourseDetailView.as_view(), name="detail"),
    path("<slug:course_slug>/delete/", CourseDeleteView.as_view(), name="delete"),
]
