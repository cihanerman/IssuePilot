import pytest
import requests

from pilot.clients import GitHubClient
from pilot.enums import RepositoryTypes
from pilot.exceptions import TooManyRequestException
from pilot.serializers import RepositorySerializer
from pilot.services import RepositoryService


@pytest.fixture
def github_client() -> GitHubClient:
    return GitHubClient()


@pytest.fixture
def repository_service() -> RepositoryService:
    return RepositoryService()


user_data = {
    "username": "test_user",
    "email": "test@gmail.com",
    "password": "test_password",
    "github_token": "test_token",
}


class CheckSuccessResponse:
    def __init__(self):
        self.json_body = [{}]
        self.status_code = 200
        self.headers = {}

    def json(self):
        return self.json_body

    def raise_for_status(self): ...


class CheckFail429Response:
    def __init__(self):
        self.json_body = [{}]
        self.status_code = 429
        self.text = "Rate limit exceeded"
        self.headers = {
            "X-RateLimit-Remaining": "0",
        }

    def json(self):
        return self.json_body

    def raise_for_status(self): ...


class CheckFailResponse:
    def __init__(self):
        self.json_body = [{}]
        self.status_code = 503
        self.text = "Service Unavailable"
        self.headers = {}

    def json(self):
        return self.json_body

    def raise_for_status(self):
        raise requests.exceptions.HTTPError


url_mapping = {
    "https://api.github.com/repos/test/test": CheckSuccessResponse,
    "https://api.github.com/repos/test/test1": CheckFail429Response,
    "https://api.github.com/repos/test/test2": CheckFailResponse,
    "https://api.github.com/repos/test/test/issues?since=2024-05-17T08:48:50.932322+00:00&per_page=1&state=open": CheckSuccessResponse,
    "https://api.github.com/repos/test/test1/issues?since=2024-05-17T08:48:50.932322+00:00&per_page=1&state=open": CheckFail429Response,
    "https://api.github.com/repos/test/test2/issues?since=2024-05-17T08:48:50.932322+00:00&per_page=1&state=open": CheckFailResponse,
    "https://api.github.com/repos/test/test/issues/1/timeline&per_page=100": CheckSuccessResponse,
    "https://api.github.com/repos/test/test1/issues/1/timeline&per_page=100": CheckFail429Response,
    "https://api.github.com/repos/test/test2/issues/1/timeline&per_page=100": CheckFailResponse,
}


def check_repository_success_mock_get(*args, **kwargs):
    klass = url_mapping.get(args[0])
    return klass()


def get_since_mock(*args, **kwargs):
    return "2024-05-17T08:48:50.932322+00:00"


def test_check_repository_success(github_client, monkeypatch):
    monkeypatch.setattr(github_client.session, "get", check_repository_success_mock_get)
    assert github_client.check_repository("test", "test", "test")


def test_check_repository_failure_429(github_client, monkeypatch):
    monkeypatch.setattr(
        github_client.session, "get", check_repository_success_mock_get, raising=True
    )

    with pytest.raises(TooManyRequestException):
        github_client.check_repository("test1", "test", "test")


def test_check_repository_failure(github_client, monkeypatch):
    monkeypatch.setattr(
        github_client.session, "get", check_repository_success_mock_get, raising=True
    )

    with pytest.raises(requests.exceptions.HTTPError):
        github_client.check_repository("test2", "test", "test")


def test_check_create_or_update_issues_success(github_client, monkeypatch):
    monkeypatch.setattr(github_client, "_get_since", get_since_mock)
    monkeypatch.setattr(
        github_client.session, "get", check_repository_success_mock_get, raising=True
    )
    assert github_client.check_create_or_update_issues("test", "test", "test")


def test_check_create_or_update_issues_failure_429(github_client, monkeypatch):
    monkeypatch.setattr(github_client, "_get_since", get_since_mock)
    monkeypatch.setattr(
        github_client.session, "get", check_repository_success_mock_get, raising=True
    )

    with pytest.raises(TooManyRequestException):
        github_client.check_create_or_update_issues("test1", "test", "test")


def test_check_create_or_update_issues_failure(github_client, monkeypatch):
    monkeypatch.setattr(github_client, "_get_since", get_since_mock)
    monkeypatch.setattr(
        github_client.session, "get", check_repository_success_mock_get, raising=True
    )

    with pytest.raises(requests.exceptions.HTTPError):
        github_client.check_create_or_update_issues("test2", "test", "test")


def test_get_issue_timeline_success(github_client, monkeypatch):
    monkeypatch.setattr(
        github_client.session, "get", check_repository_success_mock_get, raising=True
    )
    assert github_client.get_issue_timeline("test", "test", "1", "test")


def test_get_issue_timeline_failure_429(github_client, monkeypatch):
    monkeypatch.setattr(
        github_client.session, "get", check_repository_success_mock_get, raising=True
    )

    with pytest.raises(TooManyRequestException):
        github_client.get_issue_timeline("test1", "test", "1", "test")


def test_get_issue_timeline_failure(github_client, monkeypatch):
    monkeypatch.setattr(
        github_client.session, "get", check_repository_success_mock_get, raising=True
    )

    with pytest.raises(requests.exceptions.HTTPError):
        github_client.get_issue_timeline("test2", "test", "1", "test")


check_repository_map = {
    "test": True,
    "test1": False,
}


def get_repository_mock(*args, **kwargs):
    return check_repository_map.get(args[0].get("name"))


@pytest.mark.django_db
def test_get_or_create_repository_success(repository_service, monkeypatch):
    data = {
        "name": "test",
        "repository_type": RepositoryTypes.GITHUB.value,
    }
    monkeypatch.setattr(
        repository_service.client, "check_repository", get_repository_mock
    )
    repository = repository_service.get_or_create_repository(data)
    assert repository is not None


@pytest.mark.django_db
def test_get_or_create_repository_failure(repository_service, monkeypatch):
    data = {
        "name": "test1",
        "repository_type": RepositoryTypes.GITHUB.value,
    }
    monkeypatch.setattr(
        repository_service.client, "check_repository", get_repository_mock
    )
    repository = repository_service.get_or_create_repository(data)
    assert repository is None


@pytest.mark.django_db
def test_subscribe_repository_success(
    repository_service, django_user_model, monkeypatch
):
    data = {
        "name": "test",
        "repository_type": RepositoryTypes.GITHUB.value,
        "owner": "test",
    }
    monkeypatch.setattr(
        repository_service.client, "check_repository", get_repository_mock
    )

    serializer = RepositorySerializer(data=data)
    assert serializer.is_valid()
    user = django_user_model.objects.create_user(**user_data)
    is_subscribe = repository_service.subscribe_repository(
        user, serializer.validated_data
    )
    assert is_subscribe


@pytest.mark.django_db
def test_subscribe_repository_failure(
    repository_service, django_user_model, monkeypatch
):
    data = {
        "name": "test1",
        "repository_type": RepositoryTypes.GITHUB.value,
        "owner": "test",
    }
    monkeypatch.setattr(
        repository_service.client, "check_repository", get_repository_mock
    )

    serializer = RepositorySerializer(data=data)
    assert serializer.is_valid()

    user = django_user_model.objects.create_user(**user_data)
    is_subscribe = repository_service.subscribe_repository(
        user, serializer.validated_data
    )
    assert not is_subscribe
