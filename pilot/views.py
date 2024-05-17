from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from pilot.serializers import RepositorySerializer
from pilot.services import RepositoryService


class RepositoryViewSet(APIView):
    serializer_class = RepositorySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    service = RepositoryService()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_create = self.service.subscribe_repository(
            request.user, serializer.validated_data
        )
        if not is_create:
            return Response(
                {"error": "Repository not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, repo_name):
        is_delete = self.service.unsubscribe_repository(request.user, repo_name)
        if not is_delete:
            return Response(
                {"error": "Repository not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    service = RepositoryService()

    def get(self, request, repo_name, issue_id):
        history = self.service.get_issue_timeline(repo_name, request.user, issue_id)
        if history is None:
            return Response(
                {"error": "Repository not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(history, status=status.HTTP_200_OK)
