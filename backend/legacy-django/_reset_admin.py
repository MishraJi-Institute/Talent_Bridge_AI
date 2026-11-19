from django.contrib.auth import get_user_model
from getpass import getpass

U = get_user_model()
u = U.objects.get(username="mishraji")

while True:
    p1 = getpass("Enter your NEW admin password: ")
    p2 = getpass("Confirm your NEW admin password: ")
    if p1 and p1 == p2:
        break
    print("Passwords empty or do not match. Try again.")

u.set_password(p1)
u.is_superuser = True
u.is_staff = True
u.is_active = True
u.save()

u = U.objects.get(username="mishraji")
print("SUCCESS: Admin password updated.")
print("Superuser:", u.is_superuser)
print("Password verified:", u.check_password(p1))
