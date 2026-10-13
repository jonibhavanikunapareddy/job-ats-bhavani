from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=160, unique=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=160)
    logo_url = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Candidate(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="candidate_profile",
    )
    full_name = models.CharField(max_length=160)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    portfolio_url = models.URLField(blank=True)
    skills = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class JobPosting(models.Model):
    class JobType(models.TextChoices):
        FULL_TIME = "Full-time", "Full-time"
        PART_TIME = "Part-time", "Part-time"
        CONTRACT = "Contract", "Contract"
        INTERNSHIP = "Internship", "Internship"
        TEMPORARY = "Temporary", "Temporary"

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="job_postings"
    )
    title = models.CharField(max_length=160)
    location = models.CharField(max_length=160, blank=True)
    job_type = models.CharField(max_length=24, choices=JobType.choices)
    required_skills = models.CharField(max_length=500)
    salary_range = models.CharField(max_length=120, blank=True)
    description = models.TextField()
    vacancies = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-posted_at"]

    def __str__(self):
        return f"{self.title} at {self.company.name}"


class JobApplication(models.Model):
    class Status(models.TextChoices):
        APPLIED = "Applied", "Applied"
        UNDER_REVIEW = "Under Review", "Under Review"
        SHORTLISTED = "Shortlisted", "Shortlisted"
        REJECTED = "Rejected", "Rejected"

    job = models.ForeignKey(
        JobPosting, on_delete=models.CASCADE, related_name="applications"
    )
    candidate = models.ForeignKey(
        Candidate, on_delete=models.CASCADE, related_name="applications"
    )
    cover_letter = models.TextField(max_length=5000)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.APPLIED
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-applied_at"]
        constraints = [
            models.UniqueConstraint(
                fields=("job", "candidate"),
                name="unique_candidate_job_application",
            )
        ]

    def __str__(self):
        return f"{self.candidate.full_name} — {self.job.title}"
