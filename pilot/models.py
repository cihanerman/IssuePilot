from django.db import models
from pilot.enums import RepositoryTypes

# Create your models here.
class Repository(models.Model):
    """
    A class representing a repository.

    This class represents a repository in the database. It contains the repository's
    name, description, and URL.

    Attributes:
        name (str): The name of the repository.
        description (str): The description of the repository.
        url (str): The URL of the repository.
    """
    name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    users = models.ManyToManyField('users.User', related_name='repositories')
    repository_type = models.IntegerField(choices=RepositoryTypes.choices(), default=RepositoryTypes.GITHUB)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    class Meta:
        unique_together = ['name', 'repository_type']
        indexes = [
            models.Index(fields=['name'])
        ]