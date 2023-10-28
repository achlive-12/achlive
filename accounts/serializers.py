from rest_framework import serializers
from .models import Customer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('email', 'username', 'password')
    

class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)