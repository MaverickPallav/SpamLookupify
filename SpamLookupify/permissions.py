from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):                   
        if obj.owner == request.user or request.method in permissions.SAFE_METHODS:
            return True
        
        raise PermissionDenied("The requested object does not belong to you.")