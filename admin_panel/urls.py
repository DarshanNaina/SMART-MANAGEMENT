from django.urls import path

from .views import (
    assign_teachers,
    dashboard,
    delete_student_profile,
    delete_teacher_profile,
    delete_user,
    manage_classes_subjects,
    manage_profiles,
    manage_users,
)

app_name = "admin_panel"

urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("users/", manage_users, name="manage_users"),
    path("users/<int:user_id>/delete/", delete_user, name="delete_user"),
    path("profiles/", manage_profiles, name="manage_profiles"),
    path("profiles/teacher/<int:profile_id>/delete/", delete_teacher_profile, name="delete_teacher_profile"),
    path("profiles/student/<int:profile_id>/delete/", delete_student_profile, name="delete_student_profile"),
    path("classes-subjects/", manage_classes_subjects, name="manage_classes_subjects"),
    path("assign-teachers/", assign_teachers, name="assign_teachers"),
]
