from users.models import User


class UserService:
    """
    This class provides methods for creating and managing user objects.
    """

    def create_user(self, **validated_data: dict) -> User:
        """
        Creates a new user with the provided validated data.

        Args:
            validated_data (dict): A dictionary containing the validated data for the user.
        """

        user = User.objects.create_user(**validated_data)
        if github_token := validated_data.get("github_token"):
            user.set_github_token(github_token)
        return user

    def update_user(self, **validated_data: dict) -> User:
        """
        Updates an existing user with the provided validated data.

        Args:
            validated_data (dict): A dictionary containing the validated data for the user.
        """

        try:
            user = User.objects.get(username=validated_data["username"])
        except User.DoesNotExist:
            raise User.DoesNotExist(
                f"User does not exist with username {validated_data['username']}"
            )

        validated_data.pop("username")
        if github_token := validated_data.pop("github_token", None):
            user.set_github_token(github_token)
        for k, v in validated_data.items():
            setattr(user, k, v)
        user.save()
        return user
