from rest_framework import serializers
from snippets.models import Snippet, SharedSnippet, Note
from authentication.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']

class SnippetSerializer(serializers.ModelSerializer):
    snippet_id = serializers.ReadOnlyField(source = 'id')
    owner = serializers.ReadOnlyField(source = 'owner.email')
    highlight = serializers.HyperlinkedIdentityField(view_name='snippet-highlight', format= 'html')
    
    class Meta:
        model = Snippet
        fields = ['snippet_id', 'owner', 'highlight', 'title', 'code', 'description', 'linenos', 'language', 'tags' ,'style', 'deleted']
        
        
class SharedSnippetSerializer(serializers.ModelSerializer):  
    shared_snippet_id = serializers.ReadOnlyField(source = 'id')
    snippet = SnippetSerializer(read_only=True)  
    shared_with = serializers.EmailField(write_only = True )
    can_edit = serializers.BooleanField()
    
    class Meta:
        model = SharedSnippet
        fields = ['shared_snippet_id', 'snippet', 'shared_with', 'can_edit', 'shared_at']
        read_only_fields = [ 'shared_at']
        
    def validate_shared_with(self, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Use with email does not exist.')
        return user
    
    def create(self, validated_data):
        shared_with = validated_data.pop('shared_with')
        snippet = validated_data.pop('snippet')
        shared_with_user = User.objects.get(email = shared_with)
        return SharedSnippet.objects.create(snippet=snippet, shared_with=shared_with_user, **validated_data)
        
    
    
class NoteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Note
        fields = ['content', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        snippet = validated_data.pop('snippet')
        note = Note.objects.create(snippet=snippet, **validated_data)
        return note
        