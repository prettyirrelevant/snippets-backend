from django.contrib.auth import login
from knox.views import LoginView as KnoxLoginView
from rest_framework import status, mixins
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.generics import (
    ListCreateAPIView,
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    GenericAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Snippet, User, Comment
from .permissions import IsOwner
from .serializers import (
    SnippetSerializer,
    UserSerializer,
    CommentSerializer,
    UserProfileSerializer,
)


class SnippetsView(ListCreateAPIView):
    """
    List all available non-secret snippets and
    Creates a new snippet
    """

    serializer_class = SnippetSerializer
    queryset = Snippet.objects.filter(secret=False).order_by("-created_on")

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        else:
            return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "status": "success",
                "message": "Snippet created successfully",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {"status": "success", "data": serializer.data}, status=status.HTTP_200_OK
        )


class SnippetView(RetrieveUpdateDestroyAPIView):
    """
    Get, Delete, Update a particular snippet based on `uid`
    """

    serializer_class = SnippetSerializer
    queryset = Snippet
    lookup_field = "uid"

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        else:
            return [IsAuthenticated(), IsOwner()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {"status": "success", "data": serializer.data}, status=status.HTTP_200_OK
        )


class RegistrationView(CreateAPIView):
    """
    Creates a new user account
    """

    serializer_class = UserSerializer
    queryset = User

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"status": "success", "message": "Account created successfully"},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class LoginView(KnoxLoginView):
    """
    Login endpoint for users using Knox.
    """

    permission_classes = []

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)

        response = super(LoginView, self).post(request, format=None)
        return response


class CommentsView(mixins.CreateModelMixin, GenericAPIView):
    """
    Create a new comment under a given snippet
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer
    queryset = Comment

    def get_serializer_context(self):
        context = super(CommentsView, self).get_serializer_context()
        snippet_uid = self.kwargs.get("uid")
        context.update({"snippet_uid": snippet_uid})
        return context

    def post(self, *args, **kwargs):
        response = super(CommentsView, self).create(self.request, *args, **kwargs)
        return response


class CommentView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericAPIView):
    """
    Edit/Update a comment
    Delete a comment
    """

    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = CommentSerializer
    lookup_field = "id"
    queryset = Comment

    def get_serializer_context(self):
        context = super(CommentView, self).get_serializer_context()
        snippet_uid = self.kwargs.get("uid")
        context.update({"snippet_uid": snippet_uid})
        return context

    def delete(self, *args, **kwargs):
        response = super(CommentView, self).destroy(self.request, *args, **kwargs)
        return response

    def put(self, *args, **kwargs):
        response = super(CommentView, self).partial_update(
            self.request, *args, **kwargs
        )
        return response


class UserProfileView(mixins.ListModelMixin, GenericAPIView):
    """
    Returns a user profile with snippets created by the user
    """

    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    def get_queryset(self):
        if self.request.user.username == self.kwargs.get("username"):
            return User.objects.filter(username=self.kwargs.get("username"))

        else:
            return User.objects.filter(
                username=self.kwargs.get("username"), snippet__secret=False
            )

    def get(self, *args, **kwargs):
        response = super(UserProfileView, self).list(self.request, *args, **kwargs)
        return response


class StargazersView(GenericAPIView):
    queryset = Snippet.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "uid"

    def post(self, *args, **kwargs):
        user = self.request.user
        snippet: Snippet = self.get_object()
        if Snippet.objects.filter(
            uid=snippet.uid, stargazers__username=user.username
        ).exists():
            return Response(
                {"status": "error", "message": "Snippet already starred"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        snippet.stargazers.add(user)
        return Response(
            {"status": "success", "message": "Snippet starred successfully"},
            status=status.HTTP_200_OK,
        )

    def delete(self, *args, **kwargs):
        user = self.request.user
        snippet: Snippet = self.get_object()

        if not Snippet.objects.filter(
            uid=snippet.uid, stargazers__username=user.username
        ).exists():
            return Response(
                {"status": "error", "message": "Snippet not starred"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        snippet.stargazers.remove(user)
        return Response(
            {"status": "success", "message": "Snippet unstarred successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
