from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils import timezone
from django.conf import settings

from accounts.models import Attendance, CustomUser, Mark, StudentProfile, Subject, TeacherProfile, TeacherSubjectAssignment

from .forms import AssignmentForm, AttendanceForm, MarkForm


def _teacher_profile(user):
    profile, _ = TeacherProfile.objects.select_related("user").get_or_create(
        user=user,
        defaults={"employee_id": f"T-{user.id:05d}"},
    )
    return profile


def dashboard(request):
    profile = _teacher_profile(request.user)
    subject_ids = TeacherSubjectAssignment.objects.filter(teacher=profile).values_list("subject_id", flat=True)
    context = {
        "subject_count": len(subject_ids),
        "mark_count": Mark.objects.filter(subject_id__in=subject_ids, entered_by=profile).count(),
        "attendance_count": Attendance.objects.filter(subject_id__in=subject_ids, marked_by=profile).count(),
    }
    return render(request, "teacher/dashboard.html", context)


def manage_marks(request):
    profile = _teacher_profile(request.user)
    subject_ids = list(TeacherSubjectAssignment.objects.filter(teacher=profile).values_list("subject_id", flat=True))
    form = MarkForm(request.POST or None)
    form.fields["subject"].queryset = Subject.objects.filter(id__in=subject_ids)
    form.fields["student"].queryset = StudentProfile.objects.filter(academic_class__subjects__id__in=subject_ids).distinct()
    if form.is_valid():
        mark = form.save(commit=False)
        if mark.subject_id not in subject_ids:
            messages.error(request, "You can only create marks for your assigned subjects.")
        else:
            Mark.objects.update_or_create(
                student=mark.student,
                subject=mark.subject,
                exam_name=mark.exam_name,
                defaults={
                    "marks_obtained": mark.marks_obtained,
                    "total_marks": mark.total_marks,
                    "entered_by": profile,
                },
            )
            if mark.student.parent_email:
                send_mail(
                    subject=f"Mark Update - {mark.subject.name}",
                    message=(
                        f"Dear Parent,\n\n"
                        f"Marks updated for {mark.student.user.get_full_name() or mark.student.user.username}.\n"
                        f"Subject: {mark.subject.name}\n"
                        f"Exam: {mark.exam_name}\n"
                        f"Score: {mark.marks_obtained}/{mark.total_marks}\n"
                        f"Percentage: {mark.percentage}%\n"
                        f"Grade: {mark.grade}\n\n"
                        "Regards,\nSAMS"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[mark.student.parent_email],
                    fail_silently=True,
                )
            messages.success(request, "Mark saved/updated successfully.")
            return redirect("teacher:manage_marks")
    marks = Mark.objects.filter(subject_id__in=subject_ids).select_related("student__user", "subject")
    return render(request, "teacher/manage_marks.html", {"form": form, "marks": marks})


def manage_attendance(request):
    profile = _teacher_profile(request.user)
    subject_ids = list(TeacherSubjectAssignment.objects.filter(teacher=profile).values_list("subject_id", flat=True))
    initial = {"date": timezone.now().date()}
    form = AttendanceForm(request.POST or None, initial=initial)
    form.fields["subject"].queryset = Subject.objects.filter(id__in=subject_ids)
    form.fields["student"].queryset = StudentProfile.objects.filter(academic_class__subjects__id__in=subject_ids).distinct()
    if form.is_valid():
        attendance = form.save(commit=False)
        if attendance.subject_id not in subject_ids:
            messages.error(request, "You can only mark attendance for your assigned subjects.")
        else:
            Attendance.objects.update_or_create(
                student=attendance.student,
                subject=attendance.subject,
                date=attendance.date,
                defaults={"status": attendance.status, "marked_by": profile},
            )
            messages.success(request, "Attendance saved/updated.")
            return redirect("teacher:manage_attendance")
    attendance_records = Attendance.objects.filter(subject_id__in=subject_ids).select_related("student__user", "subject")
    return render(
        request,
        "teacher/manage_attendance.html",
        {"form": form, "attendance_records": attendance_records},
    )


def manage_assignments(request):
    profile = _teacher_profile(request.user)
    subject_ids = list(TeacherSubjectAssignment.objects.filter(teacher=profile).values_list("subject_id", flat=True))
    form = AssignmentForm(request.POST or None, request.FILES or None)
    form.fields["subject"].queryset = Subject.objects.filter(id__in=subject_ids)
    form.fields["academic_class"].queryset = form.fields["academic_class"].queryset.filter(subjects__id__in=subject_ids).distinct()
    if form.is_valid():
        assignment = form.save(commit=False)
        if assignment.subject_id not in subject_ids:
            messages.error(request, "You can only upload assignments for your assigned subjects.")
        else:
            assignment.uploaded_by = profile
            assignment.save()
            messages.success(request, "Assignment uploaded.")
            return redirect("teacher:manage_assignments")
    assignments = profile.assignment_set.select_related("subject", "academic_class")
    return render(request, "teacher/manage_assignments.html", {"form": form, "assignments": assignments})
