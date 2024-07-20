from rest_framework import viewsets
from snippets.serializers import *
from snippets.models import Snippet
from snippets.serializers import SnippetSerializer
from rest_framework.permissions import *
from snippets.permissions import *
from rest_framework.decorators import action
from rest_framework import renderers, status
from rest_framework.response import Response


class SnippetViewSet(viewsets.ModelViewSet):
    
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return Snippet.objects.filter(owner= self.request.user)
    
    def get_permissions(self):
        if self.action == 'highlight':
            return []
        return super().get_permissions()
        
    
    @action(detail = True, renderer_classes= [renderers.StaticHTMLRenderer], methods=['get']) 
    def highlight(self,request, pk=None):
       
        snippet = self.get_object()
        return Response(snippet.highlighted)
    
    def perform_create(self, serializer):
        serializer.save(owner= self.request.user)


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many = True)
        
        snippets_data = serializer.data
        for snippet in snippets_data:
            snippet.pop('owner', None)
            
        response_data = {
            'count': queryset.count(),
            'owner': request.user.email,
            'snippets': serializer.data    
        }
        return Response(response_data , status=status.HTTP_200_OK)
