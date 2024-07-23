from rest_framework import permissions
from snippets.models import Snippet, SharedSnippet

class IsOwnerOrReadOnly(permissions.BasePermission):
    
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user
    
class IsOwnerOrShared(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Snippet):
            if obj.owner == request.user:
                return True
            shared_snippet = SharedSnippet.objects.filter(snippet = obj, shared_with = request.user).first()
            if shared_snippet and (shared_snippet.can_edit or request.method in permissions.SAFE_METHODS):
                return True
        return False
            
    