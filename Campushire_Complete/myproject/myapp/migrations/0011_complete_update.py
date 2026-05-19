from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0010_interview'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add missing fields to Student
        migrations.AddField(
            model_name='student',
            name='internship',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name='student',
            name='projects',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='student',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='student',
            name='experience',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='student',
            name='skills',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AlterField(
            model_name='student',
            name='timings',
            field=models.CharField(blank=True, max_length=200),
        ),
        # Add missing fields to Recruiter
        migrations.AddField(
            model_name='recruiter',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='recruiter',
            name='active',
            field=models.BooleanField(default=True),
        ),
        # Add status and score to JobApplication
        migrations.AddField(
            model_name='jobapplication',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('shortlisted', 'Shortlisted'),
                    ('rejected', 'Rejected'),
                    ('hired', 'Hired'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='recruiter_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='jobapplication',
            unique_together={('student', 'job')},
        ),
        # Create Supervisor model
        migrations.CreateModel(
            name='Supervisor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(default='supervisor', max_length=20)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),
    ]
