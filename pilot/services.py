from pilot.clients import GitHubClient
from pilot.enums import RepositoryTypes
from pilot.models import Repository
from users.models import User


class RepositoryService:
    """
    Service class for managing repositories.
    """

    clients = {
        RepositoryTypes.GITHUB.value: GitHubClient(),
    }

    def get_or_create_repository(
        self, data: dict, repository_type: int = RepositoryTypes.GITHUB.value
    ) -> Repository | None:
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
            is_there = self.clients[repository_type].check_repository(
                data["name"], data["owner"], data["token"]
            )
            if not is_there:
                return None
            data.pop("token")
            repository = Repository.objects.create(**data)
        return repository

    def subscribe_repository(self, user: User, data: dict) -> bool:
        """
        Subscribes a user to a repository.

        Args:
            user: The user object.
            data (dict): A dictionary containing the repository data.
        """
        data["token"] = user.get_github_token()
        repository = self.get_or_create_repository(data)
        if not repository:
            return False
        repository.users.add(user)
        return True

    def get_issue_timeline(
        self,
        repo_name: str,
        user: User,
        issue_id: str,
        repository_type: int = RepositoryTypes.GITHUB.value,
    ) -> list | None:
        """
        Retrieves the timeline of an issue from a GitHub repository.

        Args:
            repo_name (str): The name of the repository.
            user (User): The user object.
            issue_id (str): The ID of the issue.

        Returns:
            list: A list of timeline events for the issue.

        Raises:
            None

        """
        try:
            repository = Repository.objects.get(
                name=repo_name, repository_type=repository_type
            )
        except Repository.DoesNotExist:
            return None
        return self.clients[repository_type].get_issue_timeline(
            repository.name, repository.owner, issue_id, user.get_github_token
        )

    def unsubscribe_repository(
        self, user: User, repo_name, repository_type: int = RepositoryTypes.GITHUB.value
    ) -> bool:
        """
        Unsubscribes a user from a repository.

        Args:
            user: The user object.
            data (dict): A dictionary containing the repository data.
        """
        try:
            repository = Repository.objects.get(
                name=repo_name, repository_type=repository_type
            )
        except Repository.DoesNotExist:
            return False
        repository.users.remove(user)
        return True

    def check_create_or_update_issues(
        self,
        repo_name: str,
        owner: str,
        token: str,
        repository_type: int = RepositoryTypes.GITHUB.value,
    ) -> bool:
        """
        Checks if there are any updated issues in a repository.

        Args:
            repo_name (str): The name of the repository.
            owner (str): The owner of the repository.
            token (str): The authentication token.

        Returns:
            bool: True if there are updated issues, False otherwise.
        """
        return self.clients[repository_type].check_create_or_update_issues(
            repo_name, owner, token
        )
