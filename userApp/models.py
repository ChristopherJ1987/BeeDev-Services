# accounts/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)   # 🔒 hashes password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    class Roles(models.TextChoices):
        EMPLOYEE = "EMPLOYEE", "Employee"
        CLIENT = "CLIENT", "Client"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.CLIENT)

    # Remove firstName/lastName, AbstractUser already has `first_name` and `last_name`
    # Remove password (it’s handled securely by AbstractUser)

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def fullName(self):
        return f"{self.first_name} {self.last_name}"
