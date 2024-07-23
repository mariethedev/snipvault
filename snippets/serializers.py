from rest_framework import serializers
from snippets.models import Snippet, SharedSnippet
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']

class SnippetSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source = 'owner.email')
    highlight = serializers.HyperlinkedIdentityField(view_name='snippet-highlight', format= 'html')
    
    class Meta:
        model = Snippet
        fields = ['id', 'owner', 'highlight', 'title', 'code', 'description', 'linenos', 'language', 'tags' ,'style']
        
class SharedSnippetSerializer(serializers.ModelSerializer):  
    snippet = SnippetSerializer(read_only=True)  
    shared_with = UserSerializer(read_only = True )
    
    class Meta:
        model = SharedSnippet
        fields = ['id', 'snippet', 'shared_with', 'can_edit']
        
