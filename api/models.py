from django.contrib.auth.models import AbstractUser, UserManager as AbstractUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(AbstractUserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    email = None
    profile_picture = models.CharField(_('profile picture'), max_length=188)

    objects = UserManager()

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    def stargazers_count(self):
        return self.stargazers_liked.count()


class Snippet(models.Model):
    uid = models.CharField(_('uid'), max_length=150, blank=True, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(_('name'), max_length=150, blank=True, null=False)
    description = models.CharField(_('description'), blank=True, null=True, max_length=160)
    content = models.TextField(_('content'), blank=False, null=False)
    stargazers = models.ManyToManyField(User, related_name='stargazers_liked')
    secret = models.BooleanField(_('secret'), default=False)
    created_on = models.DateTimeField(_('created on'), auto_now_add=True)
    last_updated = models.DateTimeField(_('updated on'), auto_now=True)

    def stargazers_count(self):
        return self.stargazers.count()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE, null=False, blank=False)
    message = models.TextField(_('message'), blank=False, null=False)
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
