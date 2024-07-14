from rest_framework import serializers
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(max_length = 128, min_length = 6, write_only = True, style={'input_type': 'password'})      
    
    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'email', 'password',]
        
        
    def create(self,validated_data):
        return User.objects.create_user(**validated_data)
    
    
class UserLoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length = 128,required = True, min_length = 6, write_only = True,style={'input_type': 'password'})      

    class Meta:
        model = User
        fields = ['email', 'password',]