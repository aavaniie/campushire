from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
import datetime
from .models import Student, Recruiter, Supervisor, Job, JobApplication, Interview


# ─── Landing ────────────────────────────────────────────────────────────────

def landing(request):
    return render(request, 'landing.html')


# ─── Auth ───────────────────────────────────────────────────────────────────

def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm = request.POST["confirm_password"]
        role = request.POST["role"]

        if password != confirm:
            return render(request, "signup.html", {"error": "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {"error": "Username already taken"})

        user = User.objects.create_user(username=username, email=email, password=password)

        if role == "student":
            Student.objects.create(user=user, role="student")
        elif role == "recruiter":
            Recruiter.objects.create(user=user, role="recruiter")

        messages.success(request, "Account created! Please log in.")
        return redirect("login")

    return render(request, "signup.html")


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if not user:
            return render(request, "login.html", {"error": "Invalid credentials"})

        auth_login(request, user)

        if hasattr(user, "student"):
            return redirect("student-dashboard")
        if hasattr(user, "recruiter"):
            return redirect("recruiter-dashboard")
        if hasattr(user, "supervisor"):
            return redirect("supervisor-dashboard")
        if user.is_staff or user.is_superuser:
            return redirect("/admin/")

        return redirect("landing")

    return render(request, "login.html")


@login_required
def logout_view(request):
    auth_logout(request)
    return redirect("landing")


# ─── Student ─────────────────────────────────────────────────────────────────

@login_required
def stdash(request):
    student, _ = Student.objects.get_or_create(user=request.user)

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()

        if not username:
            messages.error(request, "Username cannot be empty")
            return redirect("student-dashboard")

        if User.objects.filter(username=username).exclude(pk=request.user.pk).exists():
            messages.error(request, "That username is already taken")
            return redirect("student-dashboard")

        request.user.username = username
        request.user.email = email
        request.user.save()

        student.skills = request.POST.get("skills", "")
        student.experience = request.POST.get("experience", "")
        student.internship = request.POST.get("internship", "")
        student.projects = request.POST.get("projects", "")
        student.timings = request.POST.get("timings", "")
        student.save()

        messages.success(request, "Profile updated!")
        return redirect("student-dashboard")

    # Compute rank
    students_ordered = Student.objects.order_by('-total_marks')
    my_rank = None
    for i, s in enumerate(students_ordered, start=1):
        if s.id == student.id:
            my_rank = i
            break

    # Recent applications with their status
    my_applications = JobApplication.objects.filter(student=student).select_related('job').order_by('-applied_at')

    # Upcoming interviews
    my_interviews = Interview.objects.filter(student=student, status='scheduled').order_by('scheduled_at')[:3]

    return render(request, "student-dashboard.html", {
        "student": student,
        "my_rank": my_rank,
        "my_applications": my_applications,
        "my_interviews": my_interviews,
    })


@login_required
def profile(request):
    student, _ = Student.objects.get_or_create(user=request.user)
    students = Student.objects.order_by('-total_marks')
    rank = None
    for i, s in enumerate(students, start=1):
        if s.id == student.id:
            rank = i
            break
    return render(request, 'profile.html', {'student': student, 'rank': rank})


@login_required
def myjobs(request):
    student = get_object_or_404(Student, user=request.user)
    applied_jobs = JobApplication.objects.filter(student=student).select_related('job').order_by('-applied_at')
    saved_ids = request.session.get('saved_jobs', [])
    saved_jobs = Job.objects.filter(id__in=saved_ids)
    interviews = Interview.objects.filter(student=student).order_by('scheduled_at')
    return render(request, "my-jobs.html", {
        "applied_jobs": applied_jobs,
        "saved_jobs": saved_jobs,
        "interviews": interviews,
    })


@login_required
def my_interviews(request):
    student = get_object_or_404(Student, user=request.user)
    interviews = Interview.objects.filter(student=student).order_by('scheduled_at')
    return render(request, 'my-interviews.html', {'interviews': interviews})


@login_required
def jobs(request):
    search = request.GET.get('search', '')
    all_jobs = Job.objects.filter(is_active=True)
    if search:
        all_jobs = all_jobs.filter(
            Q(title__icontains=search) | Q(skills_required__icontains=search) | Q(company__icontains=search)
        )

    # Which jobs has the student already applied to?
    applied_job_ids = []
    if hasattr(request.user, 'student'):
        applied_job_ids = list(
            JobApplication.objects.filter(student=request.user.student).values_list('job_id', flat=True)
        )

    return render(request, "jobs.html", {"jobs": all_jobs, "search": search, "applied_job_ids": applied_job_ids})


@login_required
def apply_job(request, job_id):
    student = get_object_or_404(Student, user=request.user)
    job = get_object_or_404(Job, id=job_id)
    if not JobApplication.objects.filter(student=student, job=job).exists():
        JobApplication.objects.create(student=student, job=job)
        messages.success(request, f"Applied to {job.title}!")
    else:
        messages.info(request, "You already applied to this job.")
    return redirect('jobs')


@login_required
def save_job(request, job_id):
    saved_jobs = request.session.get('saved_jobs', [])
    if job_id not in saved_jobs:
        saved_jobs.append(job_id)
        request.session['saved_jobs'] = saved_jobs
    return redirect('jobs')


@login_required
def student_profile(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    skills_list = [s.strip() for s in student.skills.split(',')] if student.skills else []
    students_ordered = Student.objects.order_by('-total_marks')
    rank = None
    badge = ""
    for i, s in enumerate(students_ordered, start=1):
        if s.id == student.id:
            rank = i
            badge = "Top Performer" if i <= 3 else ("Rising Star" if i <= 10 else "")
            break
    return render(request, 'student-profile.html', {
        'student': student,
        'skills_list': skills_list,
        'rank': rank,
        'badge': badge,
    })


# ─── Recruiter ───────────────────────────────────────────────────────────────

@login_required
def rcdash(request):
    recruiter = get_object_or_404(Recruiter, user=request.user)
    jobs = Job.objects.filter(recruiter=request.user).order_by('-posted_at')

    job_applications = []
    for job in jobs:
        applications = JobApplication.objects.filter(job=job).select_related('student__user').order_by('-applied_at')
        job_applications.append({'job': job, 'applications': applications})

    return render(request, "recruiter-dashboard.html", {
        "recruiter": recruiter,
        "jobs": jobs,
        "job_applications": job_applications,
    })


@login_required
def postjob(request):
    if not hasattr(request.user, 'recruiter'):
        return redirect("landing")
    if request.method == "POST":
        Job.objects.create(
            recruiter=request.user,
            title=request.POST.get("title"),
            company=request.POST.get("company"),
            location=request.POST.get("location"),
            job_type=request.POST.get("job_type"),
            skills_required=request.POST.get("skills_required"),
            description=request.POST.get("description"),
            deadline=request.POST.get("deadline") or None,
        )
        messages.success(request, "Job posted successfully!")
        return redirect("recruiter-dashboard")
    return render(request, "post-job.html")


@login_required
def view_jobs(request):
    jobs = Job.objects.filter(recruiter=request.user).order_by('-posted_at')
    return render(request, "view-jobs.html", {"jobs": jobs})


@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    if request.method == "POST":
        action = request.POST.get("action", "update")
        if action == "delete":
            job.delete()
            messages.success(request, "Job deleted.")
            return redirect("view-jobs")
        job.title = request.POST.get("title")
        job.company = request.POST.get("company")
        job.location = request.POST.get("location")
        job.job_type = request.POST.get("job_type")
        job.skills_required = request.POST.get("skills_required")
        job.description = request.POST.get("description")
        job.deadline = request.POST.get("deadline") or None
        job.is_active = request.POST.get("is_active") == "on"
        job.save()
        messages.success(request, "Job updated!")
        return redirect("view-jobs")
    return render(request, "edit-job.html", {"job": job})


@login_required
def viewst(request):
    """Recruiter: view all applicants for their jobs."""
    jobs = Job.objects.filter(recruiter=request.user).order_by('-posted_at')
    job_applications = []
    for job in jobs:
        applications = JobApplication.objects.filter(job=job).select_related('student__user').order_by('-applied_at')
        job_applications.append({'job': job, 'applications': applications})
    return render(request, 'view.html', {'job_applications': job_applications})


@login_required
def update_application(request, app_id):
    """Recruiter: shortlist / reject / hire an applicant and optionally set a score."""
    app = get_object_or_404(JobApplication, id=app_id, job__recruiter=request.user)
    if request.method == "POST":
        status = request.POST.get("status")
        score = request.POST.get("score", "0")
        notes = request.POST.get("recruiter_notes", "")

        if status in dict(JobApplication.STATUS_CHOICES):
            app.status = status

        try:
            app.score = int(score)
        except (ValueError, TypeError):
            app.score = 0

        app.recruiter_notes = notes

        # If hired, mark student as placed
        if status == "hired":
            app.student.placed = True
            app.student.company = app.job.company
            app.student.save()

        app.save()
        messages.success(request, f"Application updated to '{status}'.")
    return redirect("viewst")


@login_required
def schedule_interview(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    applicants = JobApplication.objects.filter(job=job).select_related('student__user')

    if request.method == "POST":
        student_id = request.POST.get('student_id')
        datetime_str = request.POST.get('scheduled_at')
        mode = request.POST.get('mode', 'online')
        location = request.POST.get('location', '')
        notes = request.POST.get('notes', '')

        student = get_object_or_404(Student, id=student_id)
        try:
            scheduled_at = datetime.datetime.fromisoformat(datetime_str)
        except (ValueError, TypeError):
            messages.error(request, "Invalid date/time.")
            return redirect('schedule-interview', job_id=job_id)

        Interview.objects.create(
            student=student,
            job=job,
            scheduled_at=scheduled_at,
            mode=mode,
            location=location,
            notes=notes,
        )

        # Increment interview_attended count
        student.interview_attended += 1
        student.save()

        messages.success(request, f"Interview scheduled for {student.user.username}!")
        return redirect('viewst')

    return render(request, 'schedule-interview.html', {'job': job, 'applicants': applicants})


# ─── Supervisor ───────────────────────────────────────────────────────────────

def supervisor_required(view_func):
    """Decorator: only supervisors can access."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'supervisor') and not request.user.is_staff:
            messages.error(request, "Access denied.")
            return redirect("landing")
        return view_func(request, *args, **kwargs)
    return wrapper


@supervisor_required
def spdash(request):
    total_students = Student.objects.count()
    approved_students = Student.objects.filter(is_approved=True).count()
    pending_students = Student.objects.filter(is_approved=False).count()
    placed_students = Student.objects.filter(placed=True).count()
    total_recruiters = Recruiter.objects.count()
    approved_recruiters = Recruiter.objects.filter(is_approved=True).count()
    total_jobs = Job.objects.count()
    total_applications = JobApplication.objects.count()
    recent_students = Student.objects.order_by('-id')[:5]
    recent_recruiters = Recruiter.objects.order_by('-id')[:5]

    return render(request, 'supervisor-dashboard.html', {
        "total_students": total_students,
        "approved_students": approved_students,
        "pending_students": pending_students,
        "placed_students": placed_students,
        "total_recruiters": total_recruiters,
        "approved_recruiters": approved_recruiters,
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "recent_students": recent_students,
        "recent_recruiters": recent_recruiters,
    })


@supervisor_required
def verify(request):
    """Supervisor: approve / reject pending users."""
    pending_students = Student.objects.filter(is_approved=False).select_related('user')
    pending_recruiters = Recruiter.objects.filter(is_approved=False).select_related('user')
    return render(request, 'verify-users.html', {
        "pending_students": pending_students,
        "pending_recruiters": pending_recruiters,
    })


@supervisor_required
def approve_user(request, user_id, role):
    """Supervisor: approve a student or recruiter."""
    user = get_object_or_404(User, id=user_id)
    if role == 'student':
        student = get_object_or_404(Student, user=user)
        student.is_approved = True
        student.save()
        messages.success(request, f"{user.username} (student) approved.")
    elif role == 'recruiter':
        recruiter = get_object_or_404(Recruiter, user=user)
        recruiter.is_approved = True
        recruiter.save()
        messages.success(request, f"{user.username} (recruiter) approved.")
    return redirect("verify")


@supervisor_required
def reject_user(request, user_id, role):
    """Supervisor: reject (delete) a student or recruiter."""
    user = get_object_or_404(User, id=user_id)
    if role == 'student':
        Student.objects.filter(user=user).delete()
    elif role == 'recruiter':
        Recruiter.objects.filter(user=user).delete()
    user.delete()
    messages.success(request, f"User removed.")
    return redirect("verify")


@supervisor_required
def allusers(request):
    students = Student.objects.select_related('user').order_by('-total_marks')
    recruiters = Recruiter.objects.select_related('user').order_by('id')
    return render(request, 'all-users.html', {
        "students": students,
        "recruiters": recruiters,
    })


@supervisor_required
def set_student_marks(request, student_id):
    """Supervisor: set total_marks and mark as placed."""
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        try:
            marks = int(request.POST.get("total_marks", 0))
            student.total_marks = marks
        except (ValueError, TypeError):
            pass
        student.placed = request.POST.get("placed") == "on"
        student.company = request.POST.get("company", "")
        student.save()
        messages.success(request, f"Marks updated for {student.user.username}.")
    return redirect("allusers")


# ─── Leaderboard ─────────────────────────────────────────────────────────────

@login_required
def rank(request):
    students = Student.objects.order_by('-total_marks')
    my_rank = None
    for i, s in enumerate(students, start=1):
        if s.user == request.user:
            my_rank = i
        s.badge = "Top Performer" if i <= 3 else ("Rising Star" if i <= 10 else "")
    return render(request, "ranking.html", {"students": students, "my_rank": my_rank})
