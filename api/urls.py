from django.urls import path
from knox.views import LogoutView, LogoutAllView

from . import views

urlpatterns = [
    path('snippets', views.SnippetsView.as_view(), name='snippets'),
    path('snippets/<str:uid>', views.SnippetView.as_view(), name='single-snippet'),
    path('stargazers/<str:uid>', views.StargazersView.as_view(), name='star-unstar-snippet'),
    path('snippets/<str:uid>/comments', views.CommentsView.as_view(), name='create-comment'),
    path('snippets/<str:uid>/comments/<int:id>', views.CommentView.as_view(), name='update-delete-comment'),
    path('users/register', views.RegistrationView.as_view(), name='register'),
    path('users/login', views.LoginView.as_view(), name='login'),
    path('users/<str:username>', views.UserProfileView.as_view(), name='profile'),
    path('users/logout', LogoutView.as_view(), name='logout'),
    path('users/logout_all', LogoutAllView.as_view(), name='logout-all')
]
