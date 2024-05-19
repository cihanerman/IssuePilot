import logging

from django.core.mail import send_mail
from django.core.paginator import Paginator

from IssuePilot.celery import app
from IssuePilot.settings import DEFAULT_FROM_EMAIL
from pilot.enums import RepositoryTypes
from pilot.services import RepositoryService
from users.models import User

logger = logging.getLogger(__name__)

repository_services = {
    RepositoryTypes.GITHUB.value: RepositoryService,
}


@app.task(bind=True, max_retries=3, default_retry_delay=60 * 2, queue="send_email")
def send_email_for_updated_repository(
    self, repository_name: str, owner: str, email: str
) -> int:
    """
    Send an email to the user when a repository is updated.

    Args:
        repository_name (str): The name of the repository.
        email (str): The email address of the user.

    Returns:
        str: The result of the task execution. Possible values are "success" or "error".
    """
    logger.info(
        f"Task started: send_email_for_updated_repository {self.request.id}, repository_name: {repository_name}, email: {email}"
    )
    try:
        send = send_mail(
            "GitHub Repository Updated",
            f"""
                {repository_name} has been updated or created new issue. Please check the repository for more details
                https://github.com/repos/{owner}/{repository_name}/issues
            """,
            DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(
            f"Error in send_email_for_updated_repository {self.request.id}: {str(e)}"
        )
        return 0

    logger.info(
        f"Task finished: send_email_for_updated_repository {self.request.id}, repository_name: {repository_name}, email: {email}"
    )
    return send


@app.task(bind=True, max_retries=3, default_retry_delay=60 * 2, queue="default")
def check_repositories_update(
    self,
    email: str,
    token: str,
    repository_name: str,
    owner: str,
    repository_type: int = RepositoryTypes.GITHUB.value,
) -> str:
    logger.info(
        f"Task started: check_repositories_update {self.request.id}, email: {email}, repository_name: {repository_name}, owner: {owner}, repository_type: {repository_type}"
    )
    try:
        service = repository_services[repository_type]()
        is_changed = service.check_create_or_update_issues(
            repository_name, owner, token
        )
        if is_changed:
            send_email_for_updated_repository.delay(repository_name, owner, email)
    except Exception as e:
        logger.error(f"Error in check_repositories_update {self.request.id}: {str(e)}")
        return "error"

    logger.info(
        f"Task finished: check_repositories_update {self.request.id}, email: {email}, repository_name: {repository_name}, owner: {owner}, repository_type: {repository_type}"
    )
    return "success"


@app.task(bind=True, max_retries=3, default_retry_delay=60 * 2, queue="default")
def check_users_repositories_update(self) -> str:
    """
    Check for updates in users' repositories and schedule tasks to process them.

    This function retrieves all active users along with their repositories and schedules tasks
    to check for updates in each repository. It uses pagination to process users in batches
    of 100 to avoid performance issues.

    Returns:
        str: The result of the task execution. Possible values are "success" or "error".
    """
    logger.info(f"Task started: check_users_repositories_update {self.request.id}")
    try:
        users = (
            User.objects.filter(is_active=True)
            .prefetch_related("repositories")
            .order_by("id")
        )
        paginator = Paginator(users, 100)
        for page in paginator.page_range:
            users_page = paginator.get_page(page)
            for user in users_page.object_list:
                for repository in user.repositories.all():
                    check_repositories_update.delay(
                        user.email,
                        user.get_github_token(),
                        repository.name,
                        repository.owner,
                        repository.repository_type,
                    )
            if not users_page.has_next():
                break
    except Exception as e:
        logger.error(
            f"Error in check_users_repositories_update {self.request.id}: {str(e)}"
        )
        return "error"
    logger.info(f"Task finished: check_users_repositories_update {self.request.id}")
    return "success"
