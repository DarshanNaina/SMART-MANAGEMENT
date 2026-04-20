from django.urls import path

from .views import dashboard, upload_assignment

app_name = "student"

urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("upload-assignment/", upload_assignment, name="upload_assignment"),
]
