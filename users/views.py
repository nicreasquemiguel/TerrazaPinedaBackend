from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import ProfileSerializer
from .models import UserAccount, Profile

# Create your views here.
class ProfileView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProfileSerializer

    def get_object(self):
        user_id = self.kwargs['user_id']
        user = UserAccount.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)
        return profile