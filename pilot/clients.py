from abc import ABC, abstractmethod


class BaseClient(ABC):
    @abstractmethod
    def check_repository(self, name: str) -> bool:
        pass
    
    @abstractmethod
    def get_updated_issues(self, name: str) -> list:
        pass

class GitHubClient(BaseClient):
    repository_url = " https://api.github.com/repos/{owner}/{repo}"
    def check_repository(self, name: str) -> bool:
         
        return True
    
    def get_updated_issues(self, name: str) -> list:
        return []