from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, default='student')
    experience = models.CharField(max_length=200, blank=True)
    skills = models.CharField(max_length=300, blank=True)
    internship = models.CharField(max_length=300, blank=True)
    projects = models.TextField(blank=True)
    timings = models.CharField(max_length=200, blank=True)
    rank = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)
    placed = models.BooleanField(default=False)
    interview_attended = models.IntegerField(default=0)
    badge = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=100, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Recruiter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, default='recruiter')
    company_name = models.CharField(max_length=100, blank=True)
    company_website = models.CharField(max_length=200, blank=True)
    is_approved = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

    @property
    def jobs_posted_count(self):
        return Job.objects.filter(recruiter=self.user).count()


class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, default='supervisor')

    def __str__(self):
        return self.user.username


class Job(models.Model):
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=50, choices=[
        ('full-time', 'Full-time'),
        ('internship', 'Internship'),
        ('part-time', 'Part-time'),
        ('remote', 'Remote'),
    ])
    skills_required = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateField(null=True, blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} at {self.company}"


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    score = models.IntegerField(default=0)
    recruiter_notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('student', 'job')

    def __str__(self):
        return f"{self.student.user.username} -> {self.job.title}"


class Interview(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    scheduled_at = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    mode = models.CharField(max_length=50, choices=[('online', 'Online'), ('offline', 'Offline')], default='online')
    status = models.CharField(max_length=20, choices=[('scheduled', 'Scheduled'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='scheduled')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.job.title} at {self.scheduled_at}"
