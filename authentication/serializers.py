from rest_framework import serializers
from .models import User, UserProfile
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from authentication.exceptions import *
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str


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
        
        
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [ 'bio', 'location', 'birth_date', 'profile_image', ]
        
        
class ChangePasswordSerializer(serializers.ModelSerializer):
    
    current_password = serializers.CharField(required = True, min_length = 8, write_only = True,style={'input_type': 'password'})
    new_password = serializers.CharField(required = True, min_length = 8, write_only = True,style={'input_type': 'password'})
    confirm_password = serializers.CharField(required = True, min_length = 8, write_only = True,style={'input_type': 'password'})
    
    def validate_password(self,data): 
        user = self.context['request'].user 
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        #Check current password
        if not user.check_password(current_password):
            raise AuthenticationFailed()
        
        ##Checks if new password and current password are the same
        if new_password == current_password:
            raise SamePasswordException()
        
        # Check if new password and confirm password match
        if new_password != confirm_password:
            raise PasswordMismatchError()
     
        try:
            validate_password(new_password, user=user)
            
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
        return data
    
    
    class Meta:
        model = User
        fields = ['current_password', 'new_password', 'confirm_password',]
        
        
class ResetPasswordSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField(required = True)
    
    class Meta:
        model = User
        fields = ['email', ]
        
        
class PasswordResetConfirmSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(required = True, min_length = 8, write_only = True,style={'input_type': 'password'})
    confirm_password = serializers.CharField(required = True, min_length = 8, write_only = True,style={'input_type': 'password'})

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise PasswordMismatchError()

        try:
            validate_password(data['new_password'])
            
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
        return data

    def save(self, user):
        user.set_password(self.validated_data['new_password'])
        user.save()

    class Meta:
        model = User
        fields = ('new_password', 'confirm_password')