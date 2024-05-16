from enum import IntEnum


class RepositoryTypes(IntEnum):
    GITHUB = 1

    @classmethod
    def choices(cls) -> list:
        return [(tag.value, tag.name) for tag in cls]
