from django.urls import path

from pilot import views

urlpatterns = [
    path("subscribe/", views.RepositoryViewSet.as_view(), name="subscribe"),
    path(
        "unsubscribe/<str:repo_name>/",
        views.RepositoryViewSet.as_view(),
        name="unsubscribe",
    ),
    path(
        "<str:repo_name>/issues/<str:issue_id>/",
        views.IssueHistoryView.as_view(),
        name="history",
    ),
]
