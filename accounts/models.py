from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from datetime import timedelta


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        TEACHER = "TEACHER", "Teacher"
        STUDENT = "STUDENT", "Student"

    role = models.CharField(max_length=20, choices=Role.choices)

    def __str__(self):
        return f"{self.username} ({self.role})"


class AcademicClass(models.Model):
    name = models.CharField(max_length=100, unique=True)
    section = models.CharField(max_length=10, blank=True)

    class Meta:
        ordering = ["name", "section"]
        verbose_name_plural = "Academic classes"

    def __str__(self):
        return f"{self.name} {self.section}".strip()


class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    academic_class = models.ForeignKey(AcademicClass, on_delete=models.CASCADE, related_name="subjects")

    class Meta:
        unique_together = ("name", "academic_class")
        ordering = ["academic_class__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.academic_class})"


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=30, unique=True)
    parent_email = models.EmailField(blank=True)
    academic_class = models.ForeignKey(
        AcademicClass,
        on_delete=models.SET_NULL,
        related_name="students",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.roll_number} - {self.user.get_full_name() or self.user.username}"


class TeacherSubjectAssignment(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="assignments")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="teacher_assignments")

    class Meta:
        unique_together = ("teacher", "subject")

    def __str__(self):
        return f"{self.teacher} -> {self.subject}"


class Mark(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="marks")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="marks")
    exam_name = models.CharField(max_length=100, default="Term Exam")
    marks_obtained = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    total_marks = models.PositiveIntegerField(default=100)
    entered_by = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "subject", "exam_name")
        ordering = ["-created_at"]

    @property
    def percentage(self):
        if self.total_marks == 0:
            return 0
        return round((self.marks_obtained / self.total_marks) * 100, 2)

    @property
    def grade(self):
        pct = self.percentage
        if pct >= 90:
            return "A+"
        if pct >= 80:
            return "A"
        if pct >= 70:
            return "B"
        if pct >= 60:
            return "C"
        if pct >= 50:
            return "D"
        return "F"

    def __str__(self):
        return f"{self.student.roll_number} | {self.subject.name} | {self.exam_name}"


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", "Absent"

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="attendance_records")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    marked_by = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ("student", "subject", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.student.roll_number} - {self.subject.name} - {self.date}"


class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="assignments")
    academic_class = models.ForeignKey(AcademicClass, on_delete=models.CASCADE, related_name="assignments")
    uploaded_by = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to="assignments/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.academic_class}"


class OTPVerification(models.Model):
    class Purpose(models.TextChoices):
        REGISTRATION = "REGISTRATION", "Registration"
        LOGIN = "LOGIN", "Login"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otp_entries")
    purpose = models.CharField(max_length=20, choices=Purpose.choices)
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]

    @classmethod
    def get_expiry_time(cls):
        return timezone.now() + timedelta(minutes=10)

    def is_valid(self):
        return (not self.is_used) and timezone.now() <= self.expires_at


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="submissions")
    file = models.FileField(upload_to="submissions/")
    remarks = models.CharField(max_length=255, blank=True)
    submitted_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("assignment", "student")
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.student.roll_number} -> {self.assignment.title}"
