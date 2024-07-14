from rest_framework.views import APIView
from authentication.serializers import UserRegistrationSerializer
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

class UserRegisterAPIView(APIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        
        mutable_data = request.data.copy()  # Make a mutable copy of request data
        
        serializer = self.serializer_class(data=mutable_data)
        
        if serializer.is_valid():
            user = serializer.save()

            # Send email
            subject = 'Welcome to SnipVault!'
            message = 'Thank you for signing up. We are excited to have you on board!'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            send_mail(subject, message, email_from, recipient_list, fail_silently=False)

            return Response({'message': 'SignUp successful!'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
