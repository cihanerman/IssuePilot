from pilot.clients import GitHubClient
from pilot.models import Repository
from users.models import User


class RepositoryService:
    """
    Service class for managing repositories.
    """

    client = GitHubClient()

    def get_or_create_repository(self, data: dict) -> Repository | None:
        """
        Creates a new repository if it doesn't exist, or returns an existing repository.

        Args:
            data (dict): A dictionary containing the repository data.

        Returns:
            Repository: The created or existing repository object.
        """
        try:
            repository = Repository.objects.get(
                name=data["name"], repository_type=data["repository_type"]
            )
            return repository
        except Repository.DoesNotExist:
            is_there = self.client.check_repository(data)
            if not is_there:
                return None
            repository = Repository.objects.create(**data)
        return repository

    def subscribe_repository(self, user: User, data: dict) -> bool:
        """
        Subscribes a user to a repository.

        Args:
            user: The user object.
            data (dict): A dictionary containing the repository data.
        """
        repository = self.get_or_create_repository(data)
        if not repository:
            return False
        repository.users.add(user)
        return True
