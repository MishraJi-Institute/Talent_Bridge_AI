from django.contrib.auth import get_user_model
from getpass import getpass

User = get_user_model()
u = User.objects.get(username="mishraji")

while True:
    p1 = getpass("ENTER YOUR NEW PASSWORD: ")
    p2 = getpass("CONFIRM YOUR PASSWORD: ")

    if not p1:
        print("Password cannot be empty.")
    elif p1 != p2:
        print("Passwords do not match. Try again.")
    else:
        u.set_password(p1)
        u.is_superuser = True
        u.is_staff = True
        u.is_active = True
        u.save()
        print("SUCCESS: YOUR PASSWORD HAS BEEN UPDATED!")
        break
