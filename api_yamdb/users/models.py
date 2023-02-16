from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'

    ROLE_CHOICES = (
        (ADMIN, 'admin'),
        (MODERATOR, 'moderator'),
        (USER, 'user'))

    username = models.CharField(max_length=50, blank=True, null=True, unique=True)
    email = models.EmailField(verbose_name='email', unique=True)
    role = models.CharField('Роли пользователей', default=USER, choices=ROLE_CHOICES)
    bio = models.TextField('Биография', blank=True, )
    token = models.CharField(
        blank=True,
        null=True,
        max_length=150,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ('username',)

    def __str__(self):
        return "{}".format(self.username)

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        return self.role == self.USER
