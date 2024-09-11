from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token
from .models import  Profile

User = get_user_model()



class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields =['id','email','first_name','last_name','phone', 'is_superuser','password']
        authentication_classes = ['']
        permission_classes = ['']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()
    class Meta:
        model = Profile
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = UserCreateSerializer(instance.user).data
        return response
