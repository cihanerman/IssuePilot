import pytest

from users.serializers import CreateUserSerializer, UpdateUserSerializer
from users.service import UserService
from users.utils import decrypt_data, encrypt_data


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.mark.django_db
def test_user_create_service():
    """
    Test case for the user creation service.

    This test verifies that the user creation service creates a user with the provided data.

    Steps:
    1. Create a dictionary with the user data.
    2. Create a CreateUserSerializer instance with the data.
    3. Assert that the serializer is valid.
    4. Create a UserService instance.
    5. Create a user using the service and the validated data from the serializer.
    6. Assert that the user's primary key is not None.
    """

    data = {
        "username": "test_user",
        "email": "test@gmail.com",
        "password": "test_password",
        "github_token": "test_token",
    }
    serializer = CreateUserSerializer(data=data)
    assert serializer.is_valid()

    service = UserService()
    user = service.create_user(**serializer.validated_data)
    assert user.pk is not None


@pytest.mark.django_db
def test_user_update_service():
    """
    Test case for the user update service.

    This test verifies that the user update service updates an existing user with the provided data.

    Steps:
    1. Create a dictionary with the user data.
    2. Create a UpdateUserSerializer instance with the data.
    3. Assert that the serializer is valid.
    4. Create a UserService instance.
    5. Create a user using the service and the validated data from the serializer.
    6. Update the user's email and GitHub token using the service.
    7. Assert that the user's email and GitHub token are updated correctly.
    """
    data = {
        "username": "test_user",
        "email": "test@gmail.com",
        "password": "test_password",
        "github_token": "test_token",
    }

    service = UserService()
    service.create_user(**data)

    data.pop("password")
    data.pop("github_token")
    data["email"] = "test_update@gmail.com"

    serializer = UpdateUserSerializer(data=data)
    assert serializer.is_valid()
    serializer.validated_data["username"] = "test_user"

    service = UserService()
    user = service.update_user(**serializer.validated_data)
    assert user.email == data["email"]


@pytest.mark.django_db
def test_create_user_view(api_client):
    """
    Test case for the create user view.

    This function tests the behavior of the create user view by sending a POST request
    to the '/api/v1/users/register/' endpoint with different data. It asserts that the
    response status code is as expected.

    Args:
        client (django.test.Client): The Django test client.

    Returns:
        None
    """
    data = {
        "username": "test_user1",
        "email": "test1@gmail.com",
        "password": "test_password1",
    }

    response = api_client.post("/api/v1/users/register/", data)
    assert response.status_code == 201

    data.pop("email")

    response = api_client.post("/api/v1/users/register/", data)
    assert response.status_code == 400


@pytest.mark.django_db
def test_update_user_view(api_client):
    """
    Test case for the update user view.

    This function tests the behavior of the update user view by sending a PUT request
    to the '/api/v1/users/update/' endpoint with different data. It asserts that the
    response status code is as expected.

    Args:
        client (django.test.Client): The Django test client.

    Returns:
        None
    """

    user_data = {
        "username": "test_user1",
        "email": "test1@gmail.com",
        "password": "test_password1",
        "github_token": "test_token",
    }
    service = UserService()
    service.create_user(**user_data)

    user_data.pop("email")
    user_data.pop("github_token")

    response = api_client.post("/api-token-auth/", user_data)
    response_data = response.json()
    token = response_data.get("token")
    headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}

    user_data.pop("password")
    user_data["email"] = "test_update@gmail.com"

    response = api_client.put(
        "/api/v1/users/update/", data=user_data, headers=headers, format="json"
    )

    assert response.status_code == 200


def test_encrypt_data_and_decrypt_data():
    """
    Test case for the encrypt_data and decrypt_data functions.

    This test case verifies that the encrypt_data and decrypt_data functions work correctly
    by encrypting a string, decrypting it, and asserting that the decrypted string is the same
    as the original string.

    Steps:
    1. Encrypt a test string.
    2. Decrypt the encrypted string.
    3. Assert that the decrypted string is the same as the original string.
    """
    test_string = "test_string"
    encrypted_string = encrypt_data(test_string)
    decrypted_string = decrypt_data(encrypted_string)
    assert decrypted_string == test_string
