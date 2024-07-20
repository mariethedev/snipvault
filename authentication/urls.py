from django.urls import path
from authentication.views.login import UserLoginAPIView
from authentication.views.register import UserRegisterAPIView
from authentication.views.google import *
from authentication.views.github import *
from authentication.views.userprofile import *
from authentication.views.password import *
from authentication.views.logout import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    ##Email Authentication
    path('register', UserRegisterAPIView.as_view(), name = 'register-user'),
    path('login', UserLoginAPIView.as_view(), name = 'login-user'),
    
    ##Google Authentication
    path('register/google', GoogleAuthRedirect.as_view(), name = 'google-register'),
    path('login/google', GoogleAuthRedirect.as_view(), name = 'google-login'),
    path('welcome', GoogleRedirectURIView.as_view(), name='google-redirect'),
    
    ##GitHub Authentication
    path('register/github', GithubAuthView.as_view(), name = 'github-register'),
    path('login/github', GithubAuthView.as_view(), name = 'github-login'),
    path('complete/github/', GithubRedirectView.as_view(), name = 'github-redirect'),
    
    #UserProfile
    path ('profile/', UserProfileView.as_view(), name = 'user-profile'),
    path ('profile/change_password', ChangePasswordAPIView.as_view(), name = 'change-password'),
    
    #Password 
    path('password_reset', ResetPasswordAPIView.as_view(), name = 'reset-password'),
    path('password_reset/<uidb64>/<token>/', PasswordResetConfirmAPIView.as_view(), name='password-reset-confirm'),
    
    ##Logout and Token Refresh
    path('logout', LogoutView.as_view(), name = 'logout-user'),
    path('token/refresh/', TokenRefreshView.as_view(), name = 'token-refresh'),

]
