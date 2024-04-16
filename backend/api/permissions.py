from rest_framework import permissions


class IsAdminIsOwnerOrReadOnly(permissions.BasePermission):
    """
    Пользователь может изменять и удалять свои данные,
    администраторы, модераторы и суперпользователи
    могут редактировать любые данные
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
