# audit_api/permissions.py

from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает доступ на чтение всем, изменения только админам.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'admin'

class IsExpertOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ только экспертам и админам.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['expert', 'admin']

class IsParticipantOrReadOnly(permissions.BasePermission):
    """
    Разрешает доступ на чтение всем, запись только участникам (participants).
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'participant'

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ только владельцу объекта или админу.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
            
        # Для объектов, связанных с пользователем через ForeignKey
        if hasattr(obj, 'user'):
            return obj.user == request.user
            
        # Для объектов, которые сами являются пользователями
        return obj == request.user

class IsAuditParticipant(permissions.BasePermission):
    """
    Разрешает доступ только участнику связанного аудита
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.audit.participant