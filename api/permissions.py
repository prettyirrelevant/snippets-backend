from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Allows access only to creator of snippet.
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user == obj.user)
