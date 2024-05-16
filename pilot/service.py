from pilot.models import Repository
from users.models import User
from pilot.clients import GitHubClient

class RepositoryService():
    """
    Service class for managing repositories.
    """
    client = GitHubClient()

    def new_repository(self, data: dict) -> Repository:
        """
        Creates a new repository if it doesn't exist, or returns an existing repository.

        Args:
            data (dict): A dictionary containing the repository data.

        Returns:
            Repository: The created or existing repository object.
        """
        try:
            repository = Repository.objects.get(name=data['name'], repository_type=data['repository_type'])
            return repository
        except Repository.DoesNotExist:
            self.check_repository_data(data)
            repository = Repository.objects.create(**data)
        return repository
    
    def subscribe_repository(self, user: User, data: dict):
        """
        Subscribes a user to a repository.

        Args:
            user: The user object.
            data (dict): A dictionary containing the repository data.
        """
        repository = self.new_repository(**data)
        repository.users.add(user)