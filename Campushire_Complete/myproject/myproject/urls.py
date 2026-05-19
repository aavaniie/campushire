from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Public
    path('', views.landing, name="landing"),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Leaderboard (all roles)
    path('leaderboard/', views.rank, name="ranks"),

    # ── Student ──────────────────────────────────────────────────────
    path('student/dashboard/', views.stdash, name='student-dashboard'),
    path('profile/', views.profile, name="profile"),
    path('jobs/', views.jobs, name="jobs"),
    path('my-jobs/', views.myjobs, name="myjobs"),
    path('my-interviews/', views.my_interviews, name='my-interviews'),
    path('apply-job/<int:job_id>/', views.apply_job, name='apply-job'),
    path('save-job/<int:job_id>/', views.save_job, name='save-job'),
    path('student/<int:student_id>/', views.student_profile, name='student-profile'),

    # ── Recruiter ────────────────────────────────────────────────────
    path('recruiter/dashboard/', views.rcdash, name='recruiter-dashboard'),
    path('post-job/', views.postjob, name="postjob"),
    path('view-jobs/', views.view_jobs, name='view-jobs'),
    path('edit-job/<int:job_id>/', views.edit_job, name='edit-job'),
    path('applicants/', views.viewst, name="viewst"),
    path('update-application/<int:app_id>/', views.update_application, name='update-application'),
    path('schedule-interview/<int:job_id>/', views.schedule_interview, name='schedule-interview'),

    # ── Supervisor ───────────────────────────────────────────────────
    path('supervisor/dashboard/', views.spdash, name='supervisor-dashboard'),
    path('supervisor/verify-users/', views.verify, name="verify"),
    path('supervisor/all-users/', views.allusers, name="allusers"),
    path('supervisor/approve/<int:user_id>/<str:role>/', views.approve_user, name='approve-user'),
    path('supervisor/reject/<int:user_id>/<str:role>/', views.reject_user, name='reject-user'),
    path('supervisor/set-marks/<int:student_id>/', views.set_student_marks, name='set-student-marks'),
]
