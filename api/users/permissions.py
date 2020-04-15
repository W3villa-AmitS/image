from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Being Admin you can do it.
    """
    def has_permission(self, request, view=None):
        return request.user.active_role is 'A'

class IsManager(permissions.BasePermission):
    """
    Being Manager you can do it.
    """
    def has_permission(self, request, view=None):
        return request.user.active_role is 'M'

class IsSearcher(permissions.BasePermission):
    """
    Being Searcher you can do it.
    """
    def has_permission(self, request, view=None):
        return request.user.active_role is 'S'

class IsWorker(permissions.BasePermission):
    """
    Being Worker you can do it.
    """
    def has_permission(self, request, view= None):
        return request.user.active_role is 'W'

user_is_admin       =   IsAdmin().has_permission
user_is_manager     =   IsManager().has_permission
user_is_searcher    =   IsSearcher().has_permission
user_is_worker      =   IsWorker().has_permission