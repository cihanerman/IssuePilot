import pytest
import requests

from pilot.clients import GitHubClient
from pilot.exceptions import TooManyRequestException


@pytest.fixture
def github_client():
    return GitHubClient()


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
