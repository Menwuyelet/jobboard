from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'role', '').lower() == 'admin'

class IsOwnerOfInstance(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user