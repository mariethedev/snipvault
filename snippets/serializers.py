from rest_framework import serializers
from snippets.models import Snippet

class SnippetSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source = 'owner.email')
    highlight = serializers.HyperlinkedIdentityField(view_name='snippet-highlight', format= 'html')
    
    class Meta:
        model = Snippet
        fields = ['id', 'owner', 'highlight', 'title', 'code', 'description', 'linenos', 'language', 'tags' ,'style']
        
