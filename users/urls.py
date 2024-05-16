from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.CreateUserView.as_view(), name='register'),
    path('update/', views.UpdateUserView.as_view(), name='user-update'),
]