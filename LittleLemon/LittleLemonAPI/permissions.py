from rest_framework import permissions


class IsManagerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow managers to edit.
    Other users can view the items.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check if the user is in the "Managers" group.
        return request.user.groups.filter(name="Managers").exists()

    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, and OPTIONS requests to all users.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if the user is in the "Managers" group.
        return request.user.groups.filter(name="Managers").exists()


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="Managers").exists()


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.groups.exists()
