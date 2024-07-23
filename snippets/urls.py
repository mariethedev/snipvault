from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from snippets.views import SnippetViewSet, SharedSnippetViewSet
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

#SHARED SNIPPET VIEWSET
sharedsnippet_list = SharedSnippetViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

sharedsnippet_detail = SharedSnippetViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
})

urlpatterns = [
    path('', snippet_list, name = 'snippet-list'),
    path('<int:pk>/',snippet_detail , name = 'snippet-detail'),
    path('<int:pk>/highlight/', snippet_highlight, name = 'snippet-highlight'),   
    
    path('shared/', sharedsnippet_list, name = 'shared-snippet-list'),
    path('shared/<int:pk>/', sharedsnippet_detail, name = 'shared-snippet-detail'),
]



urlpatterns = format_suffix_patterns(urlpatterns)
