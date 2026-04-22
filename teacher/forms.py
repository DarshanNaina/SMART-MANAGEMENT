from django import forms

from accounts.models import Assignment, AssignmentSubmission, Attendance, Mark


class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ("student", "subject", "exam_name", "marks_obtained", "total_marks")


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ("student", "subject", "date", "status")
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ("title", "description", "subject", "academic_class", "file", "due_date")
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}


class AssignmentSubmissionMarkForm(forms.ModelForm):
    marks_obtained = forms.IntegerField(
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Marks (0-100)"}),
    )
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Feedback (optional)"}),
    )

    class Meta:
        model = AssignmentSubmission
        fields = ("marks_obtained", "remarks")
