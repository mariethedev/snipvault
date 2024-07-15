from django.conf import settings
from django.shortcuts import redirect
from django.views.generic.base import View
from rest_framework.permissions import AllowAny
from authentication.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from rest_framework import status
import requests
from authentication.exceptions import AuthorizationCodeError, GoogleAuthenticationFailed
from django.core.mail import send_mail
from django.contrib.auth import login
from django.contrib.auth.models import update_last_login


class GoogleAuthRedirect(View):
    permission_classes = [AllowAny]

    def get(self, request):
        redirect_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY}&response_type=code&scope=https://www.googleapis.com/"
            f"auth/userinfo.profile%20https://www.googleapis.com/auth/userinfo.email&access_type=offline&"
            f"redirect_uri=http://127.0.0.1:8000/welcome"
        )
        return redirect(redirect_url)


class GoogleRedirectURIView(View):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get('code')

        if not code:
            raise AuthorizationCodeError()

        # Exchange authorization code for access token
        token_endpoint = "https://oauth2.googleapis.com/token"
        token_params = {
            'code': code,
            'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
            'redirect_uri': "http://127.0.0.1:8000/welcome",
            'grant_type': 'authorization_code',
        }

        response = requests.post(token_endpoint, data=token_params)

        if response.status_code == 200:
            access_token = response.json().get('access_token')

            if access_token:
                # Use the access token to retrieve the user's information
                profile_endpoint = "https://www.googleapis.com/oauth2/v1/userinfo"
                headers = {'Authorization': f'Bearer {access_token}'}
                profile_response = requests.get(profile_endpoint, headers=headers)

                if profile_response.status_code == 200:
                    profile_data = profile_response.json()

                    # Retrieve or create user
                    user, created = User.objects.get_or_create(email=profile_data['email'], defaults={'firstname': profile_data['given_name']})

                    if created:
                        if "family_name" in profile_data:
                            user.last_name = profile_data["family_name"]
                        user.auth_provider = 'google'
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

        raise GoogleAuthenticationFailed()
