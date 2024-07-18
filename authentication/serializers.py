from rest_framework import serializers
from .models import User, UserProfile
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from authentication.exceptions import *


class UserRegistrationSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(max_length = 128, min_length = 6, write_only = True, style={'input_type': 'password'})   
    confirm_password =  serializers.CharField(max_length = 128, min_length = 6, write_only = True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'email', 'password','confirm_password',]
        
        
    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if password != confirm_password:
            raise PasswordMismatchError()
        
        user = User(email=data['email'])
        try:
            validate_password(password=password, user=user)
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User(
            email=validated_data['email'],
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    
class UserLoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length = 128,required = True, min_length = 6, write_only = True,style={'input_type': 'password'})      

    class Meta:
        model = User
        fields = ['email', 'password',]
        
        
class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source= 'user.email', read_only = True)
    
    class Meta:
        model = UserProfile
        fields = [ 'email', 'bio', 'location', 'birth_date', 'profile_image', ]
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'email': representation.pop('email'),
            'profile': representation
        }
        
        
class ChangePasswordSerializer(serializers.ModelSerializer):
    
    current_password = serializers.CharField(required = True, min_length = 8, write_only = True,style={'input_type': 'password'})
    new_password = serializers.CharField(required = True, min_length = 8, write_only = True,style={'input_type': 'password'})
    confirm_password = serializers.CharField(required = True, min_length = 8, write_only = True,style={'input_type': 'password'})
    
    def validate(self,data): 
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
            validate_password(password=new_password, user=user)
            
        except ValidationError as e:
            print(e)
            raise serializers.ValidationError({'password': list(e.detail)})
        
        return data
    
    def save(self, user):
        user = self.context['request'].user 
        user.set_password(self.validated_data['new_password'])
        user.save()
    
    
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
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if new_password != confirm_password:
            raise PasswordMismatchError()
        
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError({"user": "User context is not provided."})

        try:
            validate_password(password= new_password, user=user)
            
        except ValidationError as e:
            
            raise serializers.ValidationError({'password': list(e.messages)})
        return data
    
    
    def save(self):
        user = self.context.get('user')
        user.set_password(self.validated_data['new_password'])
        user.save()

    class Meta:
        model = User
        fields = ('new_password', 'confirm_password')
        
