from rest_framework.serializers import serializers
from pilot.models import Repository

class RepositorySerializer(serializers.ModelSerializer):
    """
    Serializer class for the Repository model.

    Serializes the Repository model fields into JSON format.

    Attributes:
        model (Model): The model class to be serialized.
        fields (list): The fields to be included in the serialized output.

    """
    class Meta:
        model = Repository
        fields = ["name", "repository_type", "owner"]