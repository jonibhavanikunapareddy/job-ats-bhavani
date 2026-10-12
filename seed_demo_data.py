import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from jobs.models import Company, JobPosting

companies = [
    {
        "name": "Northstar Labs",
        "website": "https://northstar.example",
        "location": "Austin, TX",
        "logo_url": "",
    },
    {
        "name": "Fieldwork Studio",
        "website": "https://fieldwork.example",
        "location": "Brooklyn, NY",
        "logo_url": "",
    },
    {
        "name": "Cedar Health",
        "website": "https://cedarhealth.example",
        "location": "Remote",
        "logo_url": "",
    },
]

jobs_by_company = {
    "Northstar Labs": [
        ("Product Designer", "Full-time", "Figma, research, prototyping", "$105k-$135k", 3),
        ("Frontend Engineer", "Full-time", "JavaScript, React, CSS", "$120k-$155k", 2),
    ],
    "Fieldwork Studio": [
        ("Brand Strategist", "Contract", "Research, writing, strategy", "$70-$90/hr", 1),
    ],
    "Cedar Health": [
        ("Operations Associate", "Full-time", "Operations, communication, Excel", "$65k-$82k", 4),
    ],
}

for company_data in companies:
    company, _ = Company.objects.get_or_create(
        name=company_data["name"], defaults=company_data
    )
    for title, job_type, skills, salary, vacancies in jobs_by_company[company.name]:
        JobPosting.objects.get_or_create(
            company=company,
            title=title,
            defaults={
                "job_type": job_type,
                "required_skills": skills,
                "salary_range": salary,
                "description": (
                    f"Join {company.name} as our next {title}. Work with a thoughtful, "
                    "collaborative team to build useful work with lasting impact. "
                    "We value curiosity, clear communication, and practical problem solving."
                ),
                "vacancies": vacancies,
                "is_active": True,
            },
        )

print("Demo companies and job postings are ready.")