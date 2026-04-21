from django.contrib import messages
from django.db.models import Avg
from django.shortcuts import redirect, render

from accounts.decorators import role_required
from accounts.models import Assignment, AssignmentSubmission, Attendance, CustomUser, Mark, StudentProfile
from .forms import AssignmentSubmissionForm


def _student_profile(user):
    profile, _ = StudentProfile.objects.select_related("user", "academic_class").get_or_create(
        user=user,
        defaults={"roll_number": f"S-{user.id:05d}", "academic_class": None},
    )
    return profile


@role_required(CustomUser.Role.STUDENT)
def dashboard(request):
    profile = _student_profile(request.user)
    marks = Mark.objects.filter(student=profile).select_related("subject")
    attendance_records = Attendance.objects.filter(student=profile)
    total_attendance = attendance_records.count()
    present_attendance = attendance_records.filter(status=Attendance.Status.PRESENT).count()
    attendance_percentage = round((present_attendance / total_attendance) * 100, 2) if total_attendance else 0
    average_marks = marks.aggregate(avg=Avg("marks_obtained")).get("avg") or 0
    assignments = (
        Assignment.objects.filter(academic_class=profile.academic_class).select_related("subject")[:8]
        if profile.academic_class
        else Assignment.objects.none()
    )
    context = {
        "profile": profile,
        "marks": marks,
        "assignments": assignments,
        "submission_count": AssignmentSubmission.objects.filter(student=profile).count(),
        "attendance_percentage": attendance_percentage,
        "average_marks": round(average_marks, 2),
    }
    return render(request, "student/dashboard.html", context)


@role_required(CustomUser.Role.STUDENT)
def upload_assignment(request):
    profile = _student_profile(request.user)
    form = AssignmentSubmissionForm(request.POST or None, request.FILES or None)
    form.fields["assignment"].queryset = (
        Assignment.objects.filter(academic_class=profile.academic_class).select_related("subject")
        if profile.academic_class
        else Assignment.objects.none()
    )

    if request.method == "POST" and form.is_valid():
        submission = form.save(commit=False)
        submission.student = profile
        AssignmentSubmission.objects.update_or_create(
            assignment=submission.assignment,
            student=profile,
            defaults={"file": submission.file, "remarks": submission.remarks},
        )
        messages.success(request, "Assignment submitted successfully.")
        return redirect("student:upload_assignment")

    submissions = AssignmentSubmission.objects.filter(student=profile).select_related("assignment__subject")
    return render(
        request,
        "student/upload_assignment.html",
        {"form": form, "submissions": submissions, "profile": profile},
    )
