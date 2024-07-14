from django.urls import path
from authentication.views.login import UserLoginAPIView
from authentication.views.register import UserRegisterAPIView

urlpatterns = [
    path('register', UserRegisterAPIView.as_view(), name = 'register-user'),
    path('login', UserLoginAPIView.as_view(), name = 'login-user'),

]
