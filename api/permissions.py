from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (request.user.is_staff or request.user.is_admin)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return (request.user.is_staff or request.user.is_admin)


class IsAuthorOrAdminOrModerator(permissions.BasePermission):
    def has_permission(self, request, view):

        return (
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated:
            if (request.user.is_staff or request.user.is_admin
                or request.user.is_moderator
                    or obj.author == request.user
                    or request.method == 'POST'
                    and request.user.is_authenticated):
                return True
        elif request.method in permissions.SAFE_METHODS:
            return True
