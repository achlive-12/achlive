from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse

@receiver(reset_password_token_created)
def handle_password_reset_token(sender, instance, reset_password_token, *args, **kwargs):
    user = instance.user  # Get the user associated with the token
    uid = urlsafe_base64_encode(force_bytes(user.pk))  # Encode user ID
    token = default_token_generator.make_token(user)  # Generate token

    # Construct the reset link
    reset_link = f"https://erblan.com/reset-password?token={token}&uid={uid}"

    # Send the reset link to the user's email
    subject = "Password Reset Link"
    message = f"Click the link below to reset your password:\n\n{reset_link}"
    from_email = "support@erblan.com"  # Set your sender email address
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)
