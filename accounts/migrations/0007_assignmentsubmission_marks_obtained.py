# Generated migration to add marks_obtained field to AssignmentSubmission

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_customuser_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignmentsubmission',
            name='marks_obtained',
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(100),
                ],
            ),
        ),
    ]
