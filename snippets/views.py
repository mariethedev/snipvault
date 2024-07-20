from rest_framework import viewsets, renderers, filters
from snippets.serializers import *
from snippets.models import Snippet
from snippets.serializers import SnippetSerializer
from rest_framework.permissions import *
from snippets.permissions import *
from rest_framework.decorators import action
from rest_framework import renderers, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q


class SnippetViewSet(viewsets.ModelViewSet):
    
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tags']
    search_fileds = [ 'title', 'tags', 'code']
    
    
    def get_queryset(self):
        queryset =  Snippet.objects.filter(owner= self.request.user)
        
        search = self.request.query_params.get('search', None)
        tags = self.request.query_params.get('tags', None)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(code__icontains=search) |
                Q(description__icontains=search)|
                Q(language__icontains=search)
                
            )
            
        if tags:
            tags_list = tags.split(',')
            tag_queries = Q()
            
            for tag in tags_list:
                tag = tag.strip()
                tag_queries |= Q(tags__icontains=tag)
                
            queryset = queryset.filter(tag_queries)
            
        return queryset
    
    def get_permissions(self):
        if self.action == 'highlight':
            return []
        return super().get_permissions()
        
    
    @action(detail = True, renderer_classes= [renderers.StaticHTMLRenderer], methods=['get'], permission_classes = [AllowAny]) 
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
