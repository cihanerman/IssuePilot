from users.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

class CreateUserSerializer(serializers.ModelSerializer):
    """
    Serializer class for creating a new user.

    This serializer is used to validate and serialize the data required to create a new user.
    It specifies the model and fields to be included in the serialized representation.

    Attributes:
        model (User): The User model class.
        fields (list): The list of fields to be included in the serialized representation.

    """
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email']
            )
        ]
    
    

class UpdateUserSerializer(serializers.ModelSerializer):
    """
    Serializer class for creating and updating a user.

    This serializer is used to validate and serialize the data required to create or update a user.
    It specifies the model and fields to be included in the serialized representation.

    Attributes:
        model (User): The User model class.
        fields (list): The list of fields to be included in the serialized representation.

    """
    class Meta:
        model = User
        fields = ['email', 'github_token']
        extra_kwargs = {'github_tokens': {'write_only': True}}
