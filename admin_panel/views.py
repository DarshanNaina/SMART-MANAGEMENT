from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import (
    AcademicClass,
    Assignment,
    Attendance,
    CustomUser,
    Mark,
    StudentProfile,
    Subject,
    TeacherProfile,
    TeacherSubjectAssignment,
)

from .forms import (
    ClassForm,
    StudentProfileForm,
    SubjectForm,
    TeacherAssignmentForm,
    TeacherProfileForm,
    UserCreateForm,
)


def dashboard(request):
    marks = Mark.objects.all()
    avg_percentage = round(sum(mark.percentage for mark in marks) / marks.count(), 2) if marks else 0
    attendance_total = Attendance.objects.count()
    present_total = Attendance.objects.filter(status=Attendance.Status.PRESENT).count()
    attendance_percentage = round((present_total / attendance_total) * 100, 2) if attendance_total else 0
    context = {
        "student_count": StudentProfile.objects.count(),
        "teacher_count": TeacherProfile.objects.count(),
        "class_count": AcademicClass.objects.count(),
        "subject_count": Subject.objects.count(),
        "assignment_count": Assignment.objects.count(),
        "avg_percentage": avg_percentage,
        "attendance_percentage": attendance_percentage,
        "recent_marks": marks[:8],
    }
    return render(request, "admin_panel/dashboard.html", context)


def manage_users(request):
    form = UserCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "User created successfully.")
        return redirect("admin_panel:manage_users")
    users = CustomUser.objects.exclude(is_superuser=True).order_by("username")
    return render(request, "admin_panel/manage_users.html", {"form": form, "users": users})


def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id, is_superuser=False)
    if request.method == "POST":
        user.delete()
        messages.success(request, "User deleted.")
    return redirect("admin_panel:manage_users")


def manage_classes_subjects(request):
    class_form = ClassForm(request.POST or None, prefix="class")
    subject_form = SubjectForm(request.POST or None, prefix="subject")
    if request.method == "POST":
        if "create_class" in request.POST and class_form.is_valid():
            class_form.save()
            messages.success(request, "Class created.")
            return redirect("admin_panel:manage_classes_subjects")
        if "create_subject" in request.POST and subject_form.is_valid():
            subject_form.save()
            messages.success(request, "Subject created.")
            return redirect("admin_panel:manage_classes_subjects")
    return render(
        request,
        "admin_panel/manage_classes_subjects.html",
        {
            "class_form": class_form,
            "subject_form": subject_form,
            "classes": class_form._meta.model.objects.all(),
            "subjects": Subject.objects.select_related("academic_class"),
        },
    )


def assign_teachers(request):
    form = TeacherAssignmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Teacher assigned to subject.")
        return redirect("admin_panel:assign_teachers")
    assignments = TeacherSubjectAssignment.objects.select_related("teacher__user", "subject__academic_class")
    return render(request, "admin_panel/assign_teachers.html", {"form": form, "assignments": assignments})


def manage_profiles(request):
    teacher_form = TeacherProfileForm(request.POST or None, prefix="teacher")
    student_form = StudentProfileForm(request.POST or None, prefix="student")

    if request.method == "POST":
        if "create_teacher_profile" in request.POST and teacher_form.is_valid():
            teacher_form.save()
            messages.success(request, "Teacher profile created.")
            return redirect("admin_panel:manage_profiles")
        if "create_student_profile" in request.POST and student_form.is_valid():
            student_form.save()
            messages.success(request, "Student profile created.")
            return redirect("admin_panel:manage_profiles")

    return render(
        request,
        "admin_panel/manage_profiles.html",
        {
            "teacher_form": teacher_form,
            "student_form": student_form,
            "teachers": TeacherProfile.objects.select_related("user"),
            "students": StudentProfile.objects.select_related("user", "academic_class"),
        },
    )


def delete_teacher_profile(request, profile_id):
    profile = get_object_or_404(TeacherProfile, id=profile_id)
    if request.method == "POST":
        profile.delete()
        messages.success(request, "Teacher profile deleted.")
    return redirect("admin_panel:manage_profiles")


def delete_student_profile(request, profile_id):
    profile = get_object_or_404(StudentProfile, id=profile_id)
    if request.method == "POST":
        profile.delete()
        messages.success(request, "Student profile deleted.")
    return redirect("admin_panel:manage_profiles")
