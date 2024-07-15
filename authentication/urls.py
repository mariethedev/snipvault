from django.urls import path
from authentication.views.login import UserLoginAPIView
from authentication.views.register import UserRegisterAPIView
from authentication.views.google import *
from authentication.views.github import *

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
    

]
