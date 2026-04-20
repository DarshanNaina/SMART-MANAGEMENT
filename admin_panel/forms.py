from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.models import (
    AcademicClass,
    CustomUser,
    StudentProfile,
    Subject,
    TeacherProfile,
    TeacherSubjectAssignment,
)


class UserCreateForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "first_name", "last_name", "email")


class ClassForm(forms.ModelForm):
    class Meta:
        model = AcademicClass
        fields = ("name", "section")


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ("name", "code", "academic_class")


class TeacherAssignmentForm(forms.ModelForm):
    class Meta:
        model = TeacherSubjectAssignment
        fields = ("teacher", "subject")


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ("user", "employee_id")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = CustomUser.objects.filter(role=CustomUser.Role.TEACHER)


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ("user", "roll_number", "parent_email", "academic_class")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = CustomUser.objects.filter(role=CustomUser.Role.STUDENT)
