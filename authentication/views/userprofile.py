from rest_framework import generics
from authentication.models import UserProfile
from authentication.serializers import UserProfileSerializer
from rest_framework.permissions import *


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user.userprofile
