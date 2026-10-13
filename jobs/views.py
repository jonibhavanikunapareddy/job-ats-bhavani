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


SAMPLE_JOBS = [
	{"title": "Python Developer", "company": "TCS", "location": "Hyderabad", "skills": "Python, Django, REST API", "vacancies": 5},
	{"title": "Frontend Developer", "company": "Infosys", "location": "Bangalore", "skills": "React, JavaScript", "vacancies": 3},
	{"title": "Data Analyst", "company": "Wipro", "location": "Remote", "skills": "SQL, Python, PowerBI", "vacancies": 10},
	{"title": "Java Developer", "company": "Cognizant", "location": "Chennai", "skills": "Java, Spring Boot", "vacancies": 4},
	{"title": "UI/UX Designer", "company": "Tech Mahindra", "location": "Pune", "skills": "Figma, Adobe XD", "vacancies": 2},
	{"title": "DevOps Engineer", "company": "Accenture", "location": "Hyderabad", "skills": "AWS, Docker, Jenkins", "vacancies": 3},
	{"title": "Data Scientist", "company": "IBM", "location": "Bangalore", "skills": "ML, Python", "vacancies": 2},
	{"title": "Backend Developer", "company": "Capgemini", "location": "Mumbai", "skills": "Node.js, MongoDB", "vacancies": 6},
	{"title": "Full Stack Developer", "company": "HCL", "location": "Noida", "skills": "MERN Stack", "vacancies": 5},
	{"title": "QA Engineer", "company": "Deloitte", "location": "Hyderabad", "skills": "Manual + Automation", "vacancies": 8},
	{"title": "Cloud Engineer", "company": "Amazon", "location": "Remote", "skills": "AWS, Azure", "vacancies": 4},
	{"title": "Mobile App Developer", "company": "Flipkart", "location": "Bangalore", "skills": "Flutter, Android", "vacancies": 3},
	{"title": "Business Analyst", "company": "Wipro", "location": "Chennai", "skills": "Requirement Analysis", "vacancies": 2},
	{"title": "HR Manager", "company": "TCS", "location": "Hyderabad", "skills": "Recruitment", "vacancies": 1},
	{"title": "Graphic Designer", "company": "Infosys", "location": "Pune", "skills": "Photoshop", "vacancies": 2},
	{"title": "Python Intern", "company": "Startup Hub", "location": "Remote", "skills": "Internship Python", "vacancies": 15},
	{"title": "Java Intern", "company": "Cognizant", "location": "Chennai", "skills": "Java Internship", "vacancies": 10},
	{"title": "Content Writer", "company": "Byjus", "location": "Remote", "skills": "SEO Writing", "vacancies": 5},
	{"title": "Digital Marketing", "company": "Swiggy", "location": "Hyderabad", "skills": "SEO, Ads", "vacancies": 3},
	{"title": "Sales Executive", "company": "Zomato", "location": "Mumbai", "skills": "Sales", "vacancies": 20},
	{"title": "Customer Support", "company": "Tech Mahindra", "location": "Hyderabad", "skills": "Voice Support", "vacancies": 25},
	{"title": "Network Engineer", "company": "Cisco", "location": "Bangalore", "skills": "CCNA", "vacancies": 2},
	{"title": "AI Engineer", "company": "Google", "location": "Remote", "skills": "AI, Tensorflow", "vacancies": 3},
	{"title": "Blockchain Developer", "company": "Infosys", "location": "Hyderabad", "skills": "Solidity", "vacancies": 1},
	{"title": "Cyber Security Analyst", "company": "Deloitte", "location": "Chennai", "skills": "Security", "vacancies": 2},
	{"title": "Product Manager", "company": "Microsoft", "location": "Bangalore", "skills": "Product Management", "vacancies": 1},
	{"title": "PHP Developer", "company": "Wipro", "location": "Kolkata", "skills": "PHP, Laravel", "vacancies": 4},
	{"title": "Angular Developer", "company": "TCS", "location": "Pune", "skills": "Angular", "vacancies": 3},
	{"title": "SQL Developer", "company": "Oracle", "location": "Hyderabad", "skills": "SQL, PL/SQL", "vacancies": 6},
	{"title": "WordPress Developer", "company": "Freelance", "location": "Remote", "skills": "WordPress", "vacancies": 10},
]


def _seed_sample_jobs():
	if JobPosting.objects.exists():
		return

	with transaction.atomic():
		if JobPosting.objects.exists():
			return
		for sample in SAMPLE_JOBS:
			company, _ = Company.objects.get_or_create(
				name=sample["company"],
				defaults={"location": sample["location"]},
			)
			job_type = (
				JobPosting.JobType.INTERNSHIP
				if "intern" in sample["title"].lower()
				else JobPosting.JobType.FULL_TIME
			)
			JobPosting.objects.create(
				company=company,
				title=sample["title"],
				location=sample["location"],
				job_type=job_type,
				required_skills=sample["skills"],
				description=(
					f"{sample['title']} role at {sample['company']}. "
					f"Required skills: {sample['skills']}."
				),
				vacancies=sample["vacancies"],
			)


class StyledLoginView(LoginView):
	template_name = "jobs/login.html"
	redirect_authenticated_user = True


class StyledPasswordResetView(PasswordResetView):
	template_name = "jobs/password_reset_form.html"
	email_template_name = "jobs/password_reset_email.html"
	subject_template_name = "jobs/password_reset_subject.txt"
	success_url = reverse_lazy("jobs:password_reset_done")


def job_list(request):
	_seed_sample_jobs()
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
