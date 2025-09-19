from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'role', '').lower() == 'admin'

class IsOwnerOfInstance(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.posted_by == request.user
class IsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user
class CanPost(BasePermission):
    def has_permission(self, request, view):
        return request.user.can_post_ajob