from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnlyPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and request.user == obj.author:
            return True
        return request.method in SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and request.user.is_admin:
            return True
        return request.method in SAFE_METHODS

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_admin:
            return True
        return request.method in SAFE_METHODS
