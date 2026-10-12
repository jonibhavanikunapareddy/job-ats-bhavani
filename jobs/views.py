from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordResetView
from django.db import IntegrityError, transaction
from django.db.models import IntegerField, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .forms import (
	ApplicationForm,
	CandidateProfileForm,
	CompanyForm,
	JobPostingForm,
	RegistrationForm,
)
from .models import Candidate, Company, JobApplication, JobPosting


class StyledLoginView(LoginView):
	template_name = "jobs/login.html"
	redirect_authenticated_user = True


class StyledPasswordResetView(PasswordResetView):
	template_name = "jobs/password_reset_form.html"
	email_template_name = "jobs/password_reset_email.html"
	subject_template_name = "jobs/password_reset_subject.txt"
	success_url = reverse_lazy("jobs:password_reset_done")


def job_list(request):
	jobs = (
		JobPosting.objects.filter(is_active=True)
		.select_related("company")
		.annotate(
			company_vacancies_count=Coalesce(
				Sum(
					"company__job_postings__vacancies",
					filter=Q(company__job_postings__is_active=True),
				),
				0,
				output_field=IntegerField(),
			)
		)
	)
	companies = Company.objects.annotate(
		vacancies_count=Coalesce(
			Sum("job_postings__vacancies", filter=Q(job_postings__is_active=True)),
			0,
			output_field=IntegerField(),
		)
	)
	return render(
		request,
		"jobs/job_list.html",
		{"jobs": jobs, "companies": companies, "application_form": ApplicationForm()},
	)


def job_detail(request, pk):
	job = get_object_or_404(JobPosting.objects.select_related("company"), pk=pk, is_active=True)
	existing_application = None
	if request.user.is_authenticated:
		existing_application = JobApplication.objects.filter(
			job=job, candidate__user=request.user
		).first()
	return render(
		request,
		"jobs/job_detail.html",
		{
			"job": job,
			"existing_application": existing_application,
			"application_form": ApplicationForm(),
		},
	)


@login_required
@require_POST
def apply_to_job(request, pk):
	job = get_object_or_404(JobPosting, pk=pk, is_active=True)
	candidate = get_object_or_404(Candidate, user=request.user)
	if JobApplication.objects.filter(job=job, candidate=candidate).exists():
		messages.info(request, "You have already applied for this role.")
		return redirect("jobs:job_detail", pk=job.pk)
	form = ApplicationForm(request.POST)
	if form.is_valid():
		try:
			with transaction.atomic():
				JobApplication.objects.create(
					job=job,
					candidate=candidate,
					cover_letter=form.cleaned_data["cover_letter"],
				)
		except IntegrityError:
			messages.info(request, "You have already applied for this role.")
		else:
			messages.success(request, "Your application has been submitted.")
			return redirect("jobs:profile")
	else:
		messages.error(request, "Please add a valid cover letter before applying.")
	return redirect("jobs:job_detail", pk=job.pk)


def register(request):
	if request.user.is_authenticated:
		return redirect("jobs:profile")
	form = RegistrationForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		with transaction.atomic():
			user = form.save(commit=False)
			user.email = form.cleaned_data["email"]
			user.save()
			Candidate.objects.create(
				user=user,
				full_name=form.cleaned_data["full_name"],
				email=form.cleaned_data["email"],
			)
		login(request, user)
		messages.success(request, "Your candidate account is ready.")
		return redirect("jobs:profile")
	return render(request, "jobs/register.html", {"form": form})


@login_required
def profile(request):
	candidate = get_object_or_404(Candidate, user=request.user)
	form = CandidateProfileForm(request.POST or None, instance=candidate)
	if request.method == "POST" and form.is_valid():
		candidate = form.save()
		request.user.email = candidate.email
		request.user.save(update_fields=["email"])
		messages.success(request, "Your profile has been updated.")
		return redirect("jobs:profile")
	applications = candidate.applications.select_related("job__company")
	return render(
		request,
		"jobs/profile.html",
		{"candidate": candidate, "form": form, "applications": applications},
	)


@staff_member_required(login_url="jobs:login")
def recruiter_dashboard(request):
	applications = JobApplication.objects.select_related("candidate", "job__company")
	stages = [
		(status, label, applications.filter(status=status))
		for status, label in JobApplication.Status.choices
	]
	return render(
		request,
		"jobs/dashboard.html",
		{
			"stages": stages,
			"status_choices": JobApplication.Status.choices,
			"application_count": applications.count(),
			"job_count": JobPosting.objects.count(),
		},
	)


@staff_member_required(login_url="jobs:login")
@require_POST
def update_application_status(request, pk):
	application = get_object_or_404(JobApplication, pk=pk)
	status = request.POST.get("status")
	valid_statuses = dict(JobApplication.Status.choices)
	if status in valid_statuses:
		application.status = status
		application.save(update_fields=["status"])
		messages.success(request, f"Application moved to {valid_statuses[status]}.")
	else:
		messages.error(request, "Choose a valid hiring stage.")
	return redirect("jobs:dashboard")


@staff_member_required(login_url="jobs:login")
def add_company(request):
	form = CompanyForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		form.save()
		messages.success(request, "Company added.")
		return redirect("jobs:dashboard")
	return render(request, "jobs/company_form.html", {"form": form})


@staff_member_required(login_url="jobs:login")
def add_job(request):
	form = JobPostingForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		form.save()
		messages.success(request, "Job posting added.")
		return redirect("jobs:dashboard")
	return render(request, "jobs/job_form.html", {"form": form})
