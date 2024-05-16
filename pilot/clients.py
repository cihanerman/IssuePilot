import json
import logging
from abc import ABC, abstractmethod
from datetime import timedelta

import requests
from django.core.cache import cache
from django.utils import timezone
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from pilot.enums import RepositoryTypes
from pilot.exceptions import TooManyRequestException

logger = logging.getLogger(__name__)


class BaseClient(ABC):
    """Abstract base class for client implementations."""

    @abstractmethod
    def check_repository(self, repo_name: str, owner: str, token: str) -> bool:
        """Check if a repository exists.

        Args:
            repo_name (str): The name of the repository.
            owner (str): The owner of the repository.
            token (str): The authentication token.

        Returns:
            bool: True if the repository exists, False otherwise.
        """
        pass

    @abstractmethod
    def get_updated_issues(self, repo_name: str, owner: str, token: str) -> list:
        """Get a list of updated issues in a repository.

        Args:
            repo_name (str): The name of the repository.
            owner (str): The owner of the repository.
            token (str): The authentication token.

        Returns:
            list: A list of updated issues.
        """
        pass

    @abstractmethod
    def check_update_issues(self, repo_name: str, owner: str, token: str) -> bool:
        """Check if there are any updated issues in a repository.

        Args:
            repo_name (str): The name of the repository.
            owner (str): The owner of the repository.
            token (str): The authentication token.

        Returns:
            bool: True if there are updated issues, False otherwise.
        """
        pass

    @abstractmethod
    def get_issue_timeline(
        self, repo_name: str, owner: str, issue_id: int | str, token: str
    ) -> list:
        """Get the timeline of an issue in a repository.

        Args:
            repo_name (str): The name of the repository.
            owner (str): The owner of the repository.
            issue_id (int | str): The ID of the issue.
            token (str): The authentication token.

        Returns:
            list: A list of events in the issue timeline.
        """
        pass


class GitHubClient(BaseClient):
    """
    A client class for interacting with the GitHub API.

    Attributes:
        repository_url (str): The URL template for retrieving repository information.
        issues_url (str): The URL template for retrieving issues.
        timeline_url (str): The URL template for retrieving issue timelines.
        headers (dict): The headers to be included in the API requests.

    Methods:
        __init__(): Initializes the GitHubClient class.
        _get_since(): Returns the timestamp for the past hour.
        check_repository(repo_name, owner, token): Checks if a repository exists.
        check_update_issues(repo_name, owner, token): Checks if there are any updated issues in a repository.
        get_updated_issues(repo_name, owner, token): Retrieves the updated issues in a repository.
        get_issue_timeline(repo_name, owner, issue_id, token): Retrieves the timeline of an issue in a repository.
    """

    repository_url = "https://api.github.com/repos/{owner}/{repo}"
    issues_url = "https://api.github.com/repos/{owner}/{repo}/issues?since={since}&per_page={per_page}"
    timeline_url = "https://api.github.com/repos/{owner}/{repo}/issues/{issue_id}/timeline&per_page={per_page}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    def __init__(self):
        """
        Initializes the GitHubClient class.

        It sets up the session and retry strategy for making API requests.
        """
        retry_strategy = Retry(
            total=3, status_forcelist=[500, 502, 503, 504], backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _get_since(self):
        """
        Returns the timestamp for the past hour.

        Returns:
            str: The ISO formatted timestamp for the past hour.
        """
        return (timezone.now() - timedelta(hours=1)).isoformat()

    def check_repository(self, repo_name: str, owner: str, token: str) -> bool:
        """
        Checks if a repository exists.

        Args:
            repo_name (str): The name of the repository.
            owner (str): The owner of the repository.
            token (str): The access token for authentication.

        Returns:
            bool: True if the repository exists, False otherwise.
        """
        cache_key = f"{owner}_{repo_name}"
        cache_value = cache.get(cache_key)
        if cache_value:
            return cache_value

        url = self.repository_url.format(owner=owner, repo=repo_name)
        self.headers["Authorization"] = self.headers["Authorization"].format(
            token=token
        )

        response = self.session.get(url, headers=self.headers)
        extra = {"status_code": response.status_code, "headers": response.headers}

        if response.status_code != 200:
            extra["response.text"] = response.text
        logger.info(f"Github Url: {url}", extra=extra)

        if (
            response.status_code in (429, 403)
            and response.headers.get("X-RateLimit-Remaining") == "0"
        ):
            raise TooManyRequestException(RepositoryTypes.GITHUB.name)
        response.raise_for_status()
        cache.set(cache_key, response.status_code == 200, 60)

        return response.status_code == 200

    def check_update_issues(self, repo_name: str, owner: str, token: str) -> bool:
        """
        Checks if there are any updated issues in a repository.

        Args:
            repo_name (str): The name of the repository.
            owner (str): The owner of the repository.
            token (str): The access token for authentication.

        Returns:
            bool: True if there are updated issues, False otherwise.
        """
        cache_key = f"{owner}_{repo_name}_issues"
        cache_value = cache.get(cache_key)
        if cache_value:
            return cache_value

        url = self.issues_url.format(
            owner=owner, repo=repo_name, since=self._get_since(), per_page=1
        )
        self.headers["Authorization"] = self.headers["Authorization"].format(
            token=token
        )

        response = self.session.get(url, headers=self.headers)
        extra = {"status_code": response.status_code, "headers": response.headers}

        if response.status_code != 200:
            extra["response.text"] = response.text
        logger.info(f"Github Url: {url}", extra=extra)

        if (
            response.status_code in (429, 403)
            and response.headers.get("X-RateLimit-Remaining") == "0"
        ):
            raise TooManyRequestException(RepositoryTypes.GITHUB.name)
        response.raise_for_status()

        response_data = response.json()
        result = len(response_data) > 0 and response.status_code == 200
        cache.set(cache_key, result, 60 * 60)
        return result

    def get_updated_issues(self, repo_name: str, owner: str, token: str) -> list:
        """
        Retrieves the updated issues in a repository.

        Args:
            repo_name (str): The name of the repository.
            owner (str): The owner of the repository.
            token (str): The access token for authentication.

        Returns:
            list: A list of updated issues.
        """
        cache_key = f"{owner}_{repo_name}_issues_data"
        cache_value = cache.get(cache_key)
        if cache_value:
            return json.loads(cache_value)

        url = self.issues_url.format(
            owner=owner, repo=repo_name, since=self._get_since(), per_page=100
        )
        self.headers["Authorization"] = self.headers["Authorization"].format(
            token=token
        )

        issues = []
        while url:
            response = self.session.get(url, headers=self.headers)
            logger.info(
                f"Github Url: {url}",
                extra={
                    "status_code": response.status_code,
                    "headers": response.headers,
                },
            )

            if (
                response.status_code in (429, 403)
                and response.headers.get("X-RateLimit-Remaining") == "0"
            ):
                break
            if response.status_code != 200:
                break
            issues.extend(response.json())
            links = response.headers.get("Link")

            if not links:
                break

            links = requests.utils.parse_header_links(links)
            url = {link["rel"]: link["url"] for link in links}.get("next", None)

        cache.set(cache_key, json.dumps(issues), 60 * 60)

        return issues

    def get_issue_timeline(
        self, repo_name: str, owner: str, issue_id: int | str, token: str
    ) -> list:
        """
        Retrieves the timeline of an issue in a repository.

        Args:
            repo_name (str): The name of the repository.
            owner (str): The owner of the repository.
            issue_id (int | str): The ID of the issue.
            token (str): The access token for authentication.

        Returns:
            list: A list of timeline events for the issue.
        """
        cache_key = f"{owner}_{repo_name}_{issue_id}_timeline"
        cache_value = cache.get(cache_key)
        if cache_value:
            return json.loads(cache_value)

        url = self.timeline_url.format(
            owner=owner, repo=repo_name, issue_id=issue_id, per_page=100
        )
        self.headers["Authorization"] = self.headers["Authorization"].format(
            token=token
        )

        timeline = []
        while url:
            response = self.session.get(url, headers=self.headers)
            logger.info(
                f"Github Url: {url}",
                extra={
                    "response.status_code": response.status_code,
                    "response.headers": response.headers,
                },
            )

            if (
                response.status_code in (429, 403)
                and response.headers.get("X-RateLimit-Remaining") == "0"
            ):
                break
            if response.status_code != 200:
                break
            timeline.extend(response.json())
            links = response.headers.get("Link")

            if not links:
                break

            links = requests.utils.parse_header_links(links)
            url = {link["rel"]: link["url"] for link in links}.get("next", None)

        cache.set(cache_key, json.dumps(timeline), 60 * 5)
        return timeline
