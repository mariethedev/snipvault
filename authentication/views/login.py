from rest_framework.views import APIView
from authentication.serializers import UserLoginSerializer
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from authentication.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import update_last_login



class UserLoginAPIView(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        
        if not email or not password:
            return Response({'message': 'Both email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email.strip()).first()

        if not user:
            return Response({'message': "No user with such email exists"}, status=status.HTTP_401_UNAUTHORIZED)

        elif not user.check_password(password):
            return Response({'message': 'Invalid credentials, try again'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = authenticate(request, email= email, password= password)
        
        if user is not None:
            login(request, user)
            update_last_login(None, user)
            
        else:
            return Response({'message': 'Invalid credentials, try again'}, status=status.HTTP_401_UNAUTHORIZED)
            

        serializer = self.serializer_class(user)
        response_data = serializer.data

        refresh = RefreshToken.for_user(user)
        token = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        response_data['token'] = token

        return Response(response_data, status=status.HTTP_200_OK)

