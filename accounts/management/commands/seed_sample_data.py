from django.core.management.base import BaseCommand

from accounts.models import (
    AcademicClass,
    Attendance,
    CustomUser,
    Mark,
    StudentProfile,
    Subject,
    TeacherProfile,
    TeacherSubjectAssignment,
)


class Command(BaseCommand):
    help = "Seed sample data for Smart Academic Management System"

    def handle(self, *args, **options):
        admin_user, _ = CustomUser.objects.get_or_create(
            username="admin1",
            defaults={"role": CustomUser.Role.ADMIN, "is_staff": True, "is_superuser": True},
        )
        admin_user.set_password("admin12345")
        admin_user.save()

        teacher_user, _ = CustomUser.objects.get_or_create(
            username="teacher1",
            defaults={"role": CustomUser.Role.TEACHER, "first_name": "Tina", "last_name": "Teacher"},
        )
        teacher_user.set_password("teacher12345")
        teacher_user.save()

        student_user, _ = CustomUser.objects.get_or_create(
            username="student1",
            defaults={"role": CustomUser.Role.STUDENT, "first_name": "Sam", "last_name": "Student"},
        )
        student_user.set_password("student12345")
        student_user.save()

        cls, _ = AcademicClass.objects.get_or_create(name="Grade 10", section="A")
        subject, _ = Subject.objects.get_or_create(name="Mathematics", code="MATH10", academic_class=cls)
        teacher_profile, _ = TeacherProfile.objects.get_or_create(user=teacher_user, defaults={"employee_id": "T-1001"})
        student_profile, _ = StudentProfile.objects.get_or_create(
            user=student_user,
            defaults={"roll_number": "S-1001", "academic_class": cls},
        )
        TeacherSubjectAssignment.objects.get_or_create(teacher=teacher_profile, subject=subject)
        Mark.objects.get_or_create(
            student=student_profile,
            subject=subject,
            exam_name="Unit Test 1",
            defaults={"marks_obtained": 88, "total_marks": 100, "entered_by": teacher_profile},
        )
        Attendance.objects.get_or_create(
            student=student_profile,
            subject=subject,
            status=Attendance.Status.PRESENT,
            marked_by=teacher_profile,
        )
        self.stdout.write(self.style.SUCCESS("Sample data created successfully."))
