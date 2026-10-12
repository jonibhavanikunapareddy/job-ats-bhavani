import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get("ADMIN_USERNAME", "admin")
password = os.environ.get("ADMIN_PASSWORD")

if not password:
    if os.environ.get("RENDER", "False").lower() == "true":
        sys.exit("Set ADMIN_PASSWORD in the Render environment before deploying.")
    password = "admin123"

user, created = User.objects.get_or_create(username=username)
if created:
    user.is_staff = True
    user.is_superuser = True
    user.email = os.environ.get("ADMIN_EMAIL", "")
    user.set_password(password)
    user.save()
    print(f"Created superuser '{username}'.")
elif not user.is_superuser:
    sys.exit(f"The existing user '{username}' is not a superuser; no changes made.")
else:
    print(f"Superuser '{username}' already exists; no changes made.")