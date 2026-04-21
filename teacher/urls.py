from django.urls import path

from accounts.views import register_view
from .views import dashboard, manage_assignments, manage_attendance, manage_marks

app_name = "teacher"

urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("marks/", manage_marks, name="manage_marks"),
    path("attendance/", manage_attendance, name="manage_attendance"),
    path("assignments/", manage_assignments, name="manage_assignments"),
    path("register/", register_view, {"role": "TEACHER"}, name="register"),
]
