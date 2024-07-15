from rest_framework import serializers
from .models import Customer

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('email', 'username', 'password')
    

class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

