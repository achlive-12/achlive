from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .models import Customer, Balance, Product, Invoice
from .utils import generate_unique_code, exchanged_rate, send_mail, verify_signature, check_payment_status, update_user_3, update_user, cards_mail
import requests
import uuid
from django.conf import settings
import json
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from django.http import HttpResponseBadRequest
from .models import Balance
from .serializers import BalanceSerializer
from store.serializers import ProductSerializer

class BalanceListView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]  
    def get(self, request):
        balance = Balance.objects.filter(created_by=request.user).first()
        if balance:
            serializer = BalanceSerializer(balance)
            return Response(serializer.data)
        else:
            return Response({'message': 'Balance not found'}, status=status.HTTP_404_NOT_FOUND)

@permission_classes([IsAuthenticated])
class CoinbasePaymentView(APIView):
    def get(self, request):
        # Generate a unique payment code or ID for tracking purposes
        payment_code = generate_unique_code()
        user = request.user
        user_obj = Customer.objects.get(username=user)
        user_id = user_obj.pk

        # Construct the payload with necessary information
        payload = {
            'name': 'Achlive Pay',
            'description': 'Balance Topup',
            'pricing_type': 'no_price',
            'metadata': {
                'payment_code': payment_code,
                'customer_id': user_id,
            }
        }

        # Make a POST request to create a new payment
        response = requests.post(
            'https://api.commerce.coinbase.com/charges',
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'X-CC-Api-Key': settings.COINBASE_COMMERCE_API_KEY,
                'X-CC-Version': '2018-03-22'
            }
        )

        # Check if the request to Coinbase was successful
        if response.status_code == 201:
            response_data = response.json()
            url = response_data['data']['hosted_url']
            address = response_data['data']['addresses']['bitcoin']
            txid = response_data['data']['code']

            # Check if the user already has a balance model
            balance = Balance.objects.filter(created_by=user_obj).first()
            if balance:
                balance.address = address
                balance.txid = txid
                if balance.balance is None:
                    balance.balance = 0
                balance.save()
            else:
                bits = exchanged_rate(2000)
                order_id = uuid.uuid1()
                invoice = Balance.objects.create(
                    order_id=order_id,
                    address=address,
                    txid=txid,
                    balance=0,
                    created_by=user_obj
                )

            # Save the payment code and charge object in your database or session for future reference
            return Response(
                {
                    'addr': address,
                    'bits': bits,
                    'url': url
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': 'Error creating Coinbase payment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@permission_classes([IsAuthenticated])
class BuyView(APIView):
    def get(self, request, pk):
        product_id = pk
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        price = product.price
        balance = Balance.objects.filter(created_by=request.user).first()
        
        if balance:
            b = balance.balance
            if b is not None:
                remaining = max(0, int(price - b))
            else:
                balance.balance = 0
                balance.save()
                remaining = int(price)
        else:
            remaining = price
        
        return Response({'price': price, 'remaining': remaining, 'product': ProductSerializer(product).data})
    
    def post(self, request, pk):
        product_id = pk
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        price = product.price
        balance = Balance.objects.filter(created_by=request.user).first()
        
        if not balance:
            return Response({'message': 'Balance not found'}, status=status.HTTP_404_NOT_FOUND)
        
        b = balance.balance
        check = int(price - b)
        
        if check > 0:
            return Response({'message': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
        
        balance.balance = b - price
        balance.save()
        
        if product.category.name == "Extraction":
            user = request.user
            user.verified = True
            user.save()
            send_mail(request, product)
        elif product.category.name == "Clone cards":
            product.Status = False
            product.save()
            cards_mail(request)
            return Response({'message': 'Purchase successful'}, status=status.HTTP_200_OK)
        else:
            product.Status = False
            product.save()
            send_mail(request, product)
        
        invoice = Invoice.objects.create(
            order_id=balance.order_id,
            address=balance.address,
            btcvalue=product.price,
            product=product,
            created_by=request.user,
            sold=True,
            received=product.price
        )
        
        return Response({'message': 'Purchase successful'}, status=status.HTTP_200_OK)

@authentication_classes([BasicAuthentication])
@permission_classes([AllowAny])
class CoinbaseWebhookView(APIView):
    def post(self, request):
        # Verify the request's content type
        content_type = request.META.get('CONTENT_TYPE')
        if content_type != 'application/json':
            return HttpResponseBadRequest()

        # Verify the Coinbase Commerce webhook signature
        sig_header = request.META.get('HTTP_X_CC_WEBHOOK_SIGNATURE')
        payload = request.body
        is_valid_signature = verify_signature(payload, sig_header)

        if not is_valid_signature:
            return HttpResponseBadRequest()

        # Process the webhook event
        try:
            payload = json.loads(request.body)
            event_type = payload['event']['type']
            event = payload['event']['data']
            metadata = event.get('metadata', {})

            if event_type == 'charge:confirmed':
                customer_id = metadata.get('customer_id')
                amount = float(event['pricing']['local']['amount'])
                if check_payment_status(customer_id, amount):
                    return Response(status=202)
                else:
                    return HttpResponseBadRequest()

            elif event_type == 'charge:created':
                customer_id = metadata.get('customer_id')
                invoice = Balance.objects.get(created_by=customer_id)
                username = invoice.created_by.user_name
                email = invoice.created_by.email
                return Response(status=200)

            elif event_type == 'charge:failed':
                customer_id = metadata.get('customer_id')
                invoice = Balance.objects.get(created_by=customer_id)
                username = invoice.created_by.user_name
                email = invoice.created_by.email
                amount = float(event['pricing']['local']['amount'])
                update_user_3(username, email, amount)
                return Response(status=404)

            elif event_type == 'charge:pending':
                customer_id = metadata.get('customer_id')
                invoice = Balance.objects.get(created_by=customer_id)
                username = invoice.created_by.user_name
                email = invoice.created_by.email
                amount = float(event['pricing']['local']['amount'])
                update_user(username, email, amount)
                return Response(status=200)

            # Handle other event types if needed

            return Response(status=200)

        except (KeyError, ValueError) as e:
            # Invalid payload format
            return HttpResponseBadRequest()
