from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        user = self.model(
            email=email,
            is_staff=True,
            is_superuser=True,
            **kwargs
        )
        user.set_password(password)
        user.save()
        return user


class User(AbstractUser):
    email = models.EmailField(('email address'), unique=True)
    bio = models.TextField(max_length=300, blank=True)
    confirmation_code = models.CharField(max_length=6, default='000000')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class UserRole(models.TextChoices):
        user = 'user',
        moderator = 'moderator',
        admin = 'admin',

    role = models.CharField(
        max_length=9,
        choices=UserRole.choices,
        default=UserRole.user,
    )

    @property
    def is_admin(self):
        if (self.is_staff==True or
            self.is_superuser==True or
            self.role==self.UserRole.admin):
            return True
        else:
            return False

    @property
    def is_moderator(self):
        if (self.is_admin or self.role==self.UserRole.moderator):
            return True
        else:
            return False


    objects = UserManager()
