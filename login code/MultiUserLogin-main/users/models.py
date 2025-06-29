from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.auth.hashers import make_password
from django.urls import reverse

# Custom User Model
class User(AbstractUser):
    class Types(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        FACULTY = 'FACULTY', 'Faculty'
        STUDENT = 'STUDENT', 'Student'

    type = models.CharField(max_length=50, choices=Types.choices, default=Types.STUDENT)

    def get_dashboard_url(self):
        if self.type == self.Types.ADMIN:
            return reverse('admin:index')  # Django admin panel
        return reverse('dashboard')  # shared dashboard for student/faculty

# Managers
class FacultyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=User.Types.FACULTY)

class StudentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=User.Types.STUDENT)

class AdminManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=User.Types.ADMIN)

# Proxy Models
class Faculty(User):
    objects = FacultyManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = User.Types.FACULTY
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
        faculty_group, _ = Group.objects.get_or_create(name='faculty')
        faculty_group.user_set.add(self)

class Student(User):
    objects = StudentManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = User.Types.STUDENT
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
        student_group, _ = Group.objects.get_or_create(name='student')
        student_group.user_set.add(self)

class Admin(User):
    objects = AdminManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = User.Types.ADMIN
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
