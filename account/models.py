from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class Contact(models.Model):
    user_from = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='rel_from_set', on_delete=models.CASCADE)
    user_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='rel_to_set', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'


class User(AbstractUser):
    """
    User model used project wide, defined on settings as AUTH_USER_MODEL
    """
    following = models.ManyToManyField('self',
                                       through=Contact,
                                       related_name='followers',
                                       symmetrical=False)

    def get_absolute_url(self):
        return reverse('user_detail', args=[self.username])


class Profile(models.Model):
    """
    Hold addition user details
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)

    # noinspection PyUnresolvedReferences
    def __str__(self):
        return f'Profile for: {self.user.username}'
