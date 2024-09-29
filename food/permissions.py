
# from rest_framework.permissions import BasePermission,SAFE_METHODS

# class IsAdmin(BasePermission):
#     def has_permission(self, request, view):
#         if request.user and request.user.user_role == 'admin':
#             return True
#         print(f"Permission denied for user: {request.user.user_role}")
#         return False

# class IsCustomer(BasePermission):
#     def has_permission(self, request, view):
#         if request.user and request.user.user_role == 'customer':
#             return True
#         print(f"Permission denied for user: {request.user.user_role}")
#         return False
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS requests for everyone
        if request.method in SAFE_METHODS:
            return True
        
        # Only allow POST/PUT/DELETE for admin users
        return request.user and getattr(request.user, 'user_role', None) == 'admin'
