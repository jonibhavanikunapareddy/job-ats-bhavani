from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("jobs/<int:pk>/", views.job_detail, name="job_detail"),
    path("jobs/<int:pk>/apply/", views.apply_to_job, name="apply"),
    path("register/", views.register, name="register"),
    path("login/", views.StyledLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),
    path("dashboard/", views.recruiter_dashboard, name="dashboard"),
    path("dashboard/applications/<int:pk>/status/", views.update_application_status, name="update_status"),
    path("dashboard/companies/new/", views.add_company, name="add_company"),
    path("dashboard/jobs/new/", views.add_job, name="add_job"),
    path("password-reset/", views.StyledPasswordResetView.as_view(), name="password_reset"),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="jobs/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="jobs/password_reset_confirm.html",
            success_url="/password-reset/complete/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(template_name="jobs/password_reset_complete.html"),
        name="password_reset_complete",
    ),
]