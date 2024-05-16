from users.models import User
from users.serializers import CreateUserSerializer, UpdateUserSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from users.service import UserService

class CreateUserView(APIView):
    """
    API view for creating a new user.

    This view handles the creation of a new user by accepting a POST request
    with the user data in the request body. It validates the data using the
    CreateUpdateUserSerializer and then creates a new user using the UserService.

    Attributes:
        queryset (QuerySet): The queryset of User objects.
        serializer_class (Serializer): The serializer class for creating users.
    """

    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    service = UserService()

    def post(self, request):
        """
        Handle POST requests for creating a new user.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object with the serialized user data and status code.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.service.create_user(**serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class UpdateUserView(APIView):
    """
    API view for updating an existing user.

    This view handles the updating of an existing user by accepting a PUT request
    with the user data in the request body. It validates the data using the
    UpdateUserSerializer and then updates the user using the UserService.

    Attributes:
        queryset (QuerySet): The queryset of User objects.
        serializer_class (Serializer): The serializer class for updating users.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.all()
    serializer_class = UpdateUserSerializer
    service = UserService()

    def put(self, request):
        """
        Handle PUT requests for updating an existing user.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object with the serialized user data and status code.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['username'] = request.user.username
        self.service.update_user(**serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
