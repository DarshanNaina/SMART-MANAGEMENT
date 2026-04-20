from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    AcademicClass,
    Assignment,
    Attendance,
    AssignmentSubmission,
    CustomUser,
    Mark,
    StudentProfile,
    Subject,
    TeacherProfile,
    TeacherSubjectAssignment,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_staff")


admin.site.register(AcademicClass)
admin.site.register(TeacherProfile)
admin.site.register(StudentProfile)
admin.site.register(Subject)
admin.site.register(TeacherSubjectAssignment)
admin.site.register(Mark)
admin.site.register(Attendance)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)
