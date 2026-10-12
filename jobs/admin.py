from django.contrib import admin

from .models import Candidate, Company, JobApplication, JobPosting


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
	list_display = ("name", "location", "website")
	search_fields = ("name", "location")


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
	list_display = ("title", "company", "job_type", "vacancies", "is_active", "posted_at")
	list_filter = ("job_type", "is_active", "company")
	search_fields = ("title", "required_skills", "company__name")


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
	list_display = ("full_name", "email", "phone")
	search_fields = ("full_name", "email", "skills")


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
	list_display = ("candidate", "job", "status", "applied_at")
	list_filter = ("status", "applied_at")
	search_fields = ("candidate__full_name", "job__title", "job__company__name")
from django.contrib import admin

# Register your models here.
