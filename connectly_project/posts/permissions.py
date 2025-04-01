from rest_framework.permissions import BasePermission


# Custom permission to allow only post authors to edit/delete
class IsPostAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Public posts are accessible to all authenticated users
        if obj.privacy == 'public':
            return True

        # Private posts are only accessible to the creator
        if obj.privacy == 'private':
            return obj.created_by == request.user

        # For any other privacy setting, add additional logic
        # This prevents any unintended access
        return False


class IsCommentAuthorOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (request.user.is_staff or obj.user == request.user)
    

class IsPostAuthorOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (request.user.is_staff or obj.created_by == request.user)