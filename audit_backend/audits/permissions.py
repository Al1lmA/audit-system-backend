from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'role', None) == 'admin'

class IsExpert(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'role', None) == 'expert'

class IsParticipant(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'role', None) == 'participant'

class IsExpertOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'role', None) in ['expert', 'admin']
