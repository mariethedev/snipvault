from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from snippets.views import *
from rest_framework import renderers

#SNIPPET VIEWSET
snippet_list = SnippetViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

snippet_detail = SnippetViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

snippet_highlight = SnippetViewSet.as_view({
    'get': 'highlight'},
    renderer_classes = [renderers.StaticHTMLRenderer]                                   
)


urlpatterns = [
    ##Basic Snippets Handling
    path('', snippet_list, name = 'snippet-list'),
    path('<int:pk>/',snippet_detail , name = 'snippet-detail'),
    path('<int:pk>/highlight/', snippet_highlight, name = 'snippet-highlight'),   
    
    ##Deleted Snippets Handling
    path('bin/',  DeletedSnippetsView.as_view(), name = 'deleted-snippet-list'),
    path('bin/<int:snippet_id>/restore/', RestoreDeletedSnippetView.as_view(), name = 'restore-snippet'),
    path('bin/<int:snippet_id>/delete/', PermanentlyDeleteSnippetView.as_view(), name = 'permanently-delete-snippet'),
    path('bin/clear/', PermanentlyDeleteAllSnippetsView.as_view(), name = 'clear-bin'),
    
    ##Shared Snippets Handling
    path('<int:snippet_id>/share/', ShareSnippetView.as_view(), name= 'share-snippet'),
    path('shared-snippets/', ListSharedSnippetsView.as_view(), name = 'list-shared-snippets'),
    path('shared-snippets/<int:shared_snippet_id>/edit/', EditSharedSnippetView.as_view(), name = 'edit-shared-snippet'),
    
    ##Snippets Notes Handling
    path('<int:snippet_id>/note/', NoteView.as_view(), name = 'snippet-note' ),
    
]

urlpatterns = format_suffix_patterns(urlpatterns)
