import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from jobs.models import Job
try:
    if Job.objects.count() == 0:
        Job.objects.create(title="Python Developer", company="TCS", location="Hyderabad", description="Python Django Job")
        Job.objects.create(title="React Developer", company="Infosys", location="Bangalore", description="React JS Job")
        Job.objects.create(title="Data Analyst", company="Wipro", location="Remote", description="SQL Python Job")
        print("3 Jobs Created")
    else:
        print("Jobs already exist")
except Exception as e:
    print(f"Error: {e}")
    # backup if fields different
    try:
        Job.objects.create(title="Python Developer")
        Job.objects.create(title="React Developer")
        print("Created with only title")
    except Exception as e2:
        print(e2)
