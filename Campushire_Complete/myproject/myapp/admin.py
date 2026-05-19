from django.contrib import admin
from .models import Student, Recruiter, Supervisor, Job, JobApplication, Interview


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_approved', 'total_marks', 'placed', 'badge')
    list_filter = ('is_approved', 'placed')
    search_fields = ('user__username', 'user__email')
    list_editable = ('is_approved', 'total_marks', 'placed')


@admin.register(Recruiter)
class RecruiterAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'is_approved', 'active')
    list_filter = ('is_approved', 'active')
    search_fields = ('user__username', 'company_name')
    list_editable = ('is_approved', 'active')


@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_type', 'is_active', 'posted_at', 'deadline')
    list_filter = ('is_active', 'job_type')
    search_fields = ('title', 'company')
    list_editable = ('is_active',)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'status', 'score', 'applied_at')
    list_filter = ('status',)
    search_fields = ('student__user__username', 'job__title')
    list_editable = ('status', 'score')


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'scheduled_at', 'mode', 'status')
    list_filter = ('mode', 'status')
    search_fields = ('student__user__username', 'job__title')
    list_editable = ('status',)
