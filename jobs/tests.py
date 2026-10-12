from django.core import mail
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Candidate, Company, JobApplication, JobPosting


class ATSWorkflowTests(TestCase):
	def setUp(self):
		self.company = Company.objects.create(
			name="Test Company", location="Remote", website="https://example.com"
		)
		self.job = JobPosting.objects.create(
			company=self.company,
			title="Software Engineer",
			job_type=JobPosting.JobType.FULL_TIME,
			required_skills="Python, Django, testing",
			salary_range="$100k-$120k",
			description="Build reliable products with a collaborative team.",
			vacancies=2,
		)
		self.candidate_user = User.objects.create_user(
			username="applicant", email="applicant@example.com", password="Candidate-pass-2026!"
		)
		self.candidate = Candidate.objects.create(
			user=self.candidate_user,
			full_name="Avery Applicant",
			email="applicant@example.com",
			skills="Python, Django",
		)

	def test_job_board_renders_active_listing_and_company_vacancies(self):
		response = self.client.get(reverse("jobs:job_list"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Software Engineer")
		self.assertContains(response, 'class="company-vacancies">2')
		self.assertContains(response, "open seats")

	def test_candidate_registration_creates_account_and_profile(self):
		response = self.client.post(
			reverse("jobs:register"),
			{
				"username": "newcandidate",
				"full_name": "Jordan Candidate",
				"email": "jordan@example.com",
				"password1": "A-long-unique-password-394!",
				"password2": "A-long-unique-password-394!",
			},
		)

		self.assertRedirects(response, reverse("jobs:profile"))
		self.assertTrue(Candidate.objects.filter(email="jordan@example.com").exists())

	def test_candidate_applies_once_and_sees_application(self):
		self.client.force_login(self.candidate_user)
		detail_response = self.client.get(reverse("jobs:job_detail", args=[self.job.pk]))
		self.assertEqual(detail_response.status_code, 200)
		self.assertContains(detail_response, "applicationModal")

		apply_url = reverse("jobs:apply", args=[self.job.pk])
		response = self.client.post(apply_url, {"cover_letter": "I would bring strong product engineering experience to this team."})
		self.assertRedirects(response, reverse("jobs:profile"))
		self.client.post(apply_url, {"cover_letter": "I am interested in this role and would like to contribute."})

		self.assertEqual(JobApplication.objects.filter(job=self.job, candidate=self.candidate).count(), 1)
		self.assertContains(self.client.get(reverse("jobs:profile")), "Software Engineer")

	def test_staff_can_manage_pipeline_and_candidates_cannot(self):
		application = JobApplication.objects.create(
			job=self.job,
			candidate=self.candidate,
			cover_letter="I am excited to contribute to the team.",
		)
		dashboard_url = reverse("jobs:dashboard")
		self.client.force_login(self.candidate_user)
		self.assertEqual(self.client.get(dashboard_url).status_code, 302)
		status_url = reverse("jobs:update_status", args=[application.pk])
		self.assertEqual(
			self.client.post(status_url, {"status": JobApplication.Status.SHORTLISTED}).status_code,
			302,
		)
		application.refresh_from_db()
		self.assertEqual(application.status, JobApplication.Status.APPLIED)

		recruiter = User.objects.create_user(
			username="recruiter", password="Recruiter-pass-2026!", is_staff=True
		)
		self.client.force_login(recruiter)
		dashboard_response = self.client.get(dashboard_url)
		self.assertEqual(dashboard_response.status_code, 200)
		self.assertContains(dashboard_response, "Under Review")
		update_response = self.client.post(status_url, {"status": JobApplication.Status.SHORTLISTED})
		self.assertRedirects(update_response, dashboard_url)
		application.refresh_from_db()
		self.assertEqual(application.status, JobApplication.Status.SHORTLISTED)

	def test_staff_can_add_companies_and_jobs(self):
		recruiter = User.objects.create_user(
			username="recruiter", password="Recruiter-pass-2026!", is_staff=True
		)
		self.client.force_login(recruiter)
		company_url = reverse("jobs:add_company")
		self.assertEqual(self.client.get(company_url).status_code, 200)
		response = self.client.post(
			company_url,
			{"name": "New Team", "location": "Chicago", "website": "", "logo_url": ""},
		)
		self.assertRedirects(response, reverse("jobs:dashboard"))
		new_company = Company.objects.get(name="New Team")
		job_response = self.client.post(
			reverse("jobs:add_job"),
			{
				"company": new_company.pk,
				"title": "Research Analyst",
				"job_type": JobPosting.JobType.CONTRACT,
				"required_skills": "Research, writing",
				"salary_range": "$60/hr",
				"description": "Help the team make careful decisions.",
				"vacancies": 1,
				"is_active": "on",
			},
		)
		self.assertRedirects(job_response, reverse("jobs:dashboard"))
		self.assertTrue(JobPosting.objects.filter(company=new_company, title="Research Analyst").exists())

	@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
	def test_password_reset_sends_a_confirm_link(self):
		response = self.client.post(
			reverse("jobs:password_reset"), {"email": self.candidate.email}
		)

		self.assertRedirects(response, reverse("jobs:password_reset_done"))
		self.assertEqual(len(mail.outbox), 1)
		self.assertIn("/password-reset/confirm/", mail.outbox[0].body)
from django.test import TestCase

# Create your tests here.
