from django.contrib.auth import get_user_model
from django.conf import settings
from getpass import getpass

U = get_user_model()
u = U.objects.filter(username="mishraji").first()

print("\n--- ADMIN DATABASE CHECK ---")
print("DATABASE:", settings.DATABASES["default"]["NAME"])
print("USER FOUND:", bool(u))

if u:
    print("USERNAME:", u.username)
    print("EMAIL:", u.email)
    print("SUPERUSER:", u.is_superuser)
    print("STAFF:", u.is_staff)
    print("ACTIVE:", u.is_active)
    p = getpass("Enter the password you are trying: ")
    print("PASSWORD MATCH:", u.check_password(p))
else:
    print("mishraji does not exist in this database.")
