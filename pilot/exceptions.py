from rest_framework.exceptions import APIException


class RepositoryNotFoundException(APIException):
    """
    Exception for when a repository is not found.
    """

    status_code = 404
    default_detail = "Repository not found."
    default_code = "repository_not_found"


class TooManyRequestException(APIException):
    """
    Exception for when too many requests are made.
    """

    def __init__(self, repository_type: str):
        self.default_detail = f"Too Many Request {repository_type}"

    status_code = 429
    default_code = "too_many_requests"
