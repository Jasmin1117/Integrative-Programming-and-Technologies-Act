from rest_framework.permissions import BasePermission


# Custom permission to allow only post authors to edit/delete
class IsPostAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user  # Only allow author to modify

class IsAuthorOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (request.user.is_staff or obj.created_by == request.user)
    

