from django.views.generic.base import View
from rest_framework.permissions import AllowAny
from django.conf import settings
from authentication.exceptions import *
from django.http import JsonResponse, HttpResponseRedirect
import requests
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import  login
from django.contrib.auth.models import update_last_login 
from django.core.mail import send_mail

User = get_user_model()

class GithubAuthView(View):
    permission_classes = [AllowAny]
    
    def get(self, request):
        redirect_url = (
            f"https://github.com/login/oauth/authorize?"
            f"client_id={settings.SOCIAL_AUTH_GITHUB_KEY}&"
            f"redirect_uri=http://127.0.0.1:8000/complete/github/&"
            f"scope=user:email"
        )
        return HttpResponseRedirect(redirect_url)

class GithubRedirectView(View):
    permission_classes = [AllowAny]
    
    def get(self, request):
        code = request.GET.get('code')
        
        if not code:
            raise AuthorizationCodeError()
        
        # Exchange authorization code for access token
        token_endpoint = "https://github.com/login/oauth/access_token"
        headers = {'Accept': 'application/json'}
        token_params = {
            'client_id': settings.SOCIAL_AUTH_GITHUB_KEY,
            'client_secret': settings.SOCIAL_AUTH_GITHUB_SECRET,
            'code': code,
            'redirect_uri': "http://127.0.0.1:8000/complete/github/",
        }
        
        response = requests.post(token_endpoint, headers=headers, data=token_params)
        
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            
            if access_token:
                profile_endpoint = "https://api.github.com/user"
                headers = {'Authorization': f'token {access_token}'}
                profile_response = requests.get(profile_endpoint, headers=headers)
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    
                    #Handle email retrieval
                    email = profile_data.get('email')
                    
                    if not email:
                        email_endpoint = "https://api.github.com/user/emails"
                        email_response = requests.get(email_endpoint,headers=headers)
                        if email_response.status_code == 200:
                            email_data = email_response.json()
                            email = next((item['email'] for item in email_data if item['primary']), None)
                        if not email:
                            return JsonResponse({"error": "Email not available from GitHub"}, status=400)
                        
                    
                    #Handle name retrieval
                    name = profile_data.get('name', '')
                    
                    if name:
                        full_name = name.split()
                        first_name = full_name[0]
                        last_name = full_name[1] if len(full_name)> 1 else ''
                    else:
                        first_name = profile_data['login']
                        last_name = ''
                        
                    # Retrieve or create user
                    user, created = User.objects.get_or_create(
                        email=email,
                        defaults={'firstname': first_name, 'lastname': last_name}
                    )
                    
                    if created:
                        user.auth_provider = 'github'
                        user.save()
                        
                        # Send a welcome email for new users
                        subject = 'Welcome to SnipVault!'
                        message = f'Greetings, {user.firstname}! \n\nThank you for signing up. We are excited to have you on board!'
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [user.email]
                        
                        send_mail(subject, message, email_from, recipient_list, fail_silently=False)

                        
                    # Manually update last_login for new or existing user
                    user.backend = 'django.contrib.auth.backends.ModelBackend'  # Set the backend for login
                    login(request, user)
                    update_last_login(None, user)
                    
                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user)
                    data = {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }
                    
                    
                    if created:
                        return JsonResponse(data, status=status.HTTP_201_CREATED)
                    else:
                        return JsonResponse(data, status=status.HTTP_200_OK)
                
                return JsonResponse({"error": "Failed to retrieve user profile"}, status=400)
            return JsonResponse({"error": "Failed to retrieve access token"}, status=400)
        return JsonResponse({"error": "Failed to exchange code for access token"}, status=400)
