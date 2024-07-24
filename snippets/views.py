from rest_framework import viewsets, renderers, filters
from snippets.serializers import *
from snippets.models import Snippet, SharedSnippet, Note
from snippets.serializers import SnippetSerializer, SharedSnippetSerializer , NoteSerializer
from rest_framework.permissions import *
from snippets.permissions import *
from rest_framework.decorators import action
from rest_framework import renderers, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.generics import *
from authentication.models import User
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.parsers import JSONParser





class SnippetViewSet(viewsets.ModelViewSet):
    
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly, IsOwnerOrShared]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tags']
    search_fileds = [ 'title', 'tags', 'code', 'language']
    
    
    def get_queryset(self):
        user  = self.request.user
        owned_snippets = Snippet.objects.filter(owner = user)
        shared_snippets = Snippet.objects.filter(shared_snippet__shared_with = user)
        queryset = owned_snippets | shared_snippets
        
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
        
        response_data = {
            'count': queryset.count(),
            'owner': request.user.email,
            'snippets': serializer.data    
        }
        return Response(response_data , status=status.HTTP_200_OK)



class ShareSnippetView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, snippet_id):
        try:
            snippet = Snippet.objects.get(id=snippet_id, owner=request.user)
        except Snippet.DoesNotExist:
            return Response({'error': 'Snippet not found or you do not have access to this snippet'}, status=404)

        serializer = SharedSnippetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            shared_with_email = request.data.get('shared_with')
            try:
                shared_with = User.objects.get(email=shared_with_email)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)

            if SharedSnippet.objects.filter(snippet=snippet, shared_with=shared_with).exists():
                return Response({'error': 'Snippet already shared with this user'}, status=400)

            serializer.save(snippet=snippet, shared_with=shared_with)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    
    
class ListSharedSnippetsView(ListAPIView):
    serializer_class = SharedSnippetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SharedSnippet.objects.filter(shared_with=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            'count': queryset.count(),
            'shared_snippets': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    
class EditSharedSnippetView(UpdateAPIView):
    serializer_class = SnippetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        
        shared_snippet_id = self.kwargs.get('shared_snippet_id')
        try:
            shared_snippet = SharedSnippet.objects.get(id=shared_snippet_id)
        except SharedSnippet.DoesNotExist:
            raise NotFound("Shared snippet not found.")
    
        if not (shared_snippet.can_edit and shared_snippet.shared_with == self.request.user):
            raise PermissionDenied("You do not have permission to edit this snippet.")
        
        return shared_snippet.snippet
    
    def update(self,request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': 'Shared snippet updated successfully!',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def perform_update(self, serializer):
        serializer.save()
        
        
class NoteView(APIView):
    
    permission_classes = [ IsAuthenticated]
    
    def get(self, request, snippet_id):
        note = get_object_or_404(Note, snippet_id= snippet_id)
        serializer = NoteSerializer(note)
        return Response(serializer.data)
    
    def post(self, request, snippet_id):
        
        snippet = get_object_or_404(Snippet, id=snippet_id)
        if Note.objects.filter(snippet=snippet).exists():
            return Response({"error": "A note already exists for this snippet."}, status=status.HTTP_400_BAD_REQUEST)
        
        if snippet.owner != request.user:
            return Response({"error": "You do not have permission to create a note for this snippet."}, status=status.HTTP_403_FORBIDDEN)
        
        data = JSONParser().parse(request)
        serializer = NoteSerializer(data=data)
        if serializer.is_valid():
            serializer.save(snippet=snippet)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def put(self, request, snippet_id):
        note = get_object_or_404(Note, snippet_id= snippet_id)
        if note.snippet.owner != request.user:
            return Response({"error": "You do not have permission to edit this note."}, status=status.HTTP_403_FORBIDDEN)
        
        data = JSONParser().parse(request)
        serializer = NoteSerializer(note,data=data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": "Snippet note updated successfully!",
                'data':serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

