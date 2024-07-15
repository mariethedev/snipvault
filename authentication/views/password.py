from rest_framework.views import APIView

from authentication.serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from authentication.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from authentication.exceptions import *

class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        user = request.user

        serializer = self.serializer_class(data=request.data, context={'request': request})

        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({'success': 'Password changed successfully!'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            users = User.objects.filter(email=email)

            if users.exists():
                for user in users:
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    reset_link = f"{request.scheme}://{request.get_host()}/password_reset/{uid}/{token}/"

                    # Send reset email
                    subject = 'SnipVault Password Reset Request'
                    message = f'Click the following link to reset your password: {reset_link}'
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [user.email]
                    send_mail(subject, message, email_from, recipient_list, fail_silently=False)

                return Response({'success': 'A reset link has been sent to the entered email.'}, status=status.HTTP_200_OK)

            else:
                raise UserDoesNotExistError()

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class PasswordResetConfirmAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    
    def post(self, request,uidb64= None,token = None):
        
        try:
            uid =force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid token or user ID'}, status=status.HTTP_400_BAD_REQUEST)

        if user is not None and default_token_generator.check_token(user, token):
            serializer = self.serializer_class(data=request.data)
            
            if serializer.is_valid():
                
                serializer.save(user)
                return Response({'success': 'Password reset successfully!'}, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error': 'Invalid token or user ID'}, status=status.HTTP_400_BAD_REQUEST)
    
    
