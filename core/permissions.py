from rest_framework.permissions import BasePermission

class IsMaintainer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff