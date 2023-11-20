from rest_framework import permissions

class FilePermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True
        return False
