import requests
import random
import string
import hashlib, hmac
from .models import Balance
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
def generate_unique_code():
    # Generate a random alphanumeric code of length 10
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return code

def exchanged_rate(amount):
    url = "https://www.blockonomics.co/api/price?currency=USD"
    r = requests.get(url)
    response = r.json()
    return amount/response['price']

def send_mail(request,product):
    if not product.name == "Decryptor":
        from_email = "Orders@Blacknet.net"

        to_email = request.user.email
        subject = 'Order confirmation'
        text_content = 'Thank you for the order!'
        html_content = render_to_string('account/email_notify_customer.html', {'order': product})

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
    else:
        from_email = "Orders@Blacknet.net"

        to_email = request.user.email
        subject = 'Order confirmation'
        text_content = 'Thank you for the order!'
        html_content = render_to_string('account/test_email.html', {'order': product})

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()

def verify_signature(payload, sig_header):
    secret = 'a48084b4-859f-4b10-a366-a0c4a3f02f57'  # Replace with your actual webhook secret

    if not all([payload, sig_header, secret]):
        return False

    expected_sig = compute_signature(payload, secret)

    if not secure_compare(expected_sig, sig_header):
        return False

    # Signature verification successful
    return True

def compute_signature(payload, secret):
    secret_bytes = bytes(secret, 'utf-8')
    signature = hmac.new(secret_bytes, payload, hashlib.sha256).hexdigest()
    return signature

def secure_compare(sig1, sig2):
    return hmac.compare_digest(sig1, sig2)

def update_user(username,email,amount):
        from_email = "Orders@Blacknet.net"
        username = username
        to_email = email
        subject = 'Charge Pending'
        text_content = 'Transaction Pending'
        html_content = render_to_string('account/balance_notify_customer.html',{'amount':amount,'user':username})

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        
def update_user_2(username,email,amount):
    from_email = "Orders@Blacknet.net"
    to_email = email
    subject = 'Balance Updated'
    text_content = 'Transaction successful'
    html_content = render_to_string('account/balance_notify_customer2.html',{'amount':amount,'user':username})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

def update_user_1(username,email,amount):
    from_email = "Orders@Blacknet.net"
    to_email = email
    subject = 'Balance Updated'
    text_content = 'Transaction successful'
    html_content = render_to_string('account/balance_notify_customer1.html',{'amount':amount,'user':username})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
    
def update_user_3(username,email,amount):
    from_email = "Orders@Blacknet.net"
    to_email = email
    subject = 'Charge Failed'
    text_content = 'Transaction failed'
    html_content = render_to_string('account/balance_notify_customer3.html',{'amount':amount,'user':username})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

def check_payment_status(customer_id, amount):
    
    # Retrieve the payment code and payment ID from your database or session

    try:
        invoice = Balance.objects.get(created_by=customer_id)
        invoice.balance += amount
        invoice.received = 1
        invoice.save()
        username = invoice.created_by.username
        email = invoice.created_by.email
        update_user_2(username,email,amount)
        return True
    except Balance.DoesNotExist:
        
        return False

def check_payment_status_1(customer_id, amount):
    
    # Retrieve the payment code and payment ID from your database or session

    try:
        invoice = Balance.objects.get(created_by=customer_id)
        return True
    except Balance.DoesNotExist:
        
        return False

def cards_mail(request):
    from_email = "Orders@Blacknet.net"

    to_email = request.user.email
    subject = 'Order confirmation'
    text_content = 'Thank you for the order!'
    html_content = render_to_string('account/cards_notify.html')

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()