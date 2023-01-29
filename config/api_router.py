from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from unite_compress.files.api.views import FileViewSet
from unite_compress.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("files", FileViewSet)

app_name = "api"
urlpatterns = router.urls + [
    path(
        "file-upload/",
        include("unite_compress.files.api.urls", namespace="file-upload"),
    ),
]
