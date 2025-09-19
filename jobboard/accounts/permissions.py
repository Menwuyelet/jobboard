from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'role', '').lower() == 'admin'

class IsOwnerOfApplication(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user== request.user
class IsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user
class CanPost(BasePermission):
    def has_permission(self, request, view):
        return request.user.can_post_ajob
    
class IsJobOwner(BasePermission):
    def has_permission(self, request, view):
        # Ensure the user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # obj here will be the Job instance
        return obj.posted_by == request.user

class IsJobOwnerOfApplication(BasePermission):
    def has_object_permission(self, request, view, obj):
        # obj here will be the Job instance
        return obj.job.posted_by == request.user