from rest_framework import status
from rest_framework.generics import *
from rest_framework.response import Response
from .models import Customer
from rest_framework.authtoken.models import Token
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login, logout
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from payment.models import Invoice
from payment.serializers import InvoiceSerializer

class RegistrationView(CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        # Generate an activation token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
       
        
        # Send an activation email
        current_site = get_current_site(request)
        mail_subject = 'Activate your account'
        message = render_to_string('account/registration/account_activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': uid,
            'token': token,
        })
        to_email = user.email
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()

         # Get the authentication token
        auth_token, _ = Token.objects.get_or_create(user=user)

        # Include the token key in the response data
        response_data = {
            'message': 'User registered successfully',
            'token': auth_token.key  # Serialize the token key as a string
        }

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user = serializer.save()
        user.is_active = False
        user.set_password(serializer.validated_data['password'])
        user.save()
        

        return user

class AccountActivate(GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Customer.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Customer.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return Response({"message": "Account activated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Activation failed"}, status=status.HTTP_400_BAD_REQUEST)
        
class UserLoginView(CreateAPIView):
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = Customer.objects.get(email=email)
            if user.is_active:
                pass
            else:
                return Response({"message": "Account not activated"}, status=status.HTTP_400_BAD_REQUEST)
        except Customer.DoesNotExist:
            raise AuthenticationFailed(detail="Invalid Email")

        user = authenticate(username=email, password=password)
        if user is None:
            raise AuthenticationFailed(detail="Invalid password")

        token, _ = Token.objects.get_or_create(user=user)

        # Log the user in within the session
        login(request, user)

        return Response({"message": "Login successful", "token": token.key}, status=status.HTTP_200_OK)

class UserLogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        logout(request)
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

class DashboardView(ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        invoices = Invoice.objects.filter(sold=True, created_by=user, received__gte=0)
        return invoices

