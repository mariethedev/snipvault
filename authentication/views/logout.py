from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        try:
            refresh_token = request.data['refresh']
            if not refresh_token:
                return Response({"message": "'refresh' token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({'message': 'Successfully logged out!'}, status=status.HTTP_205_RESET_CONTENT)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
