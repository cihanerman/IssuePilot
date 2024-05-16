from django.contrib.auth.models import AbstractUser
from django.db import models  # noqa
from django.utils.translation import gettext_lazy as _

from users.utils import decrypt_data, encrypt_data


# Create your models here.
class User(AbstractUser):
    """
    Custom user model representing a user in the system.
    Inherits from Django's AbstractUser class.
    """

    email = models.EmailField(_("email address"), unique=True)
    github_token = models.CharField(max_length=255, blank=True, null=True)

    def set_github_token(self, token: str):
        """
        Sets the GitHub token for the user.

        Args:
            token (str): The GitHub token to be set.
        """
        token = encrypt_data(token)
        self.github_token = token
        self.save()

    def get_github_token(self) -> str:
        """
        Retrieves the decrypted GitHub token for the user.

        Returns:
            str: The decrypted GitHub token.
        """
        return decrypt_data(self.github_token)
