from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from .serializers import ProfileSerializer
from .models import UserAccount, Profile

# Create your views here.
class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProfileSerializer

    def get_object(self):
        user_id = self.kwargs['user_id']
        user = UserAccount.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)
        print(profile.total_events)
        return profile
    
    def patch(self, request, *args, **kwargs):

        payload = request.data
        user = UserAccount.objects.get(id=payload["user_id"])

        user.first_name = payload["first_name"]
        user.last_name = payload["last_name"]
        user.phone = payload["phone"]
        user.email = payload["email"]
        user.save()

        return Response({"message": "Profile changed successfully"}, status=status.HTTP_200_OK)