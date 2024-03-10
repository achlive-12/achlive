from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .models import Balance, Product, Invoice
from .utils import  exchanged_rate, send_mail, update_admins, update_user_2, update_user_3, cards_mail, update_user
import requests
import uuid
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
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
            return Response({'message': 'Balance not found',"balance":0.00}, status=status.HTTP_404_NOT_FOUND)

class CoinbasePaymentView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated] 
    def get(self, request):
        api_key = 'f2qchMQe1X3MaEaGNyK5qr1p1vJRCzetaXZ7gylpVS0'
        amount = float(1.00)
        url = 'https://www.blockonomics.co/api/new_address'
        headers = {'Authorization': "Bearer " + api_key}
        r = requests.post(url, headers=headers)
        if r.status_code == 200:
            address = r.json()['address']
            bits = exchanged_rate(amount)
            order_id = uuid.uuid1()
            # Check if the user already has a balance model
            balance = Balance.objects.filter(created_by=request.user).first()
            if balance:
                # If the user has a balance model, use its id
                invoice_id = balance.id
                balance.address = address
                balance.received = 0
                balance.save()
                if balance.balance is None:
                    balance.balance = 0
                    balance.save()
                
            else:
                # Otherwise, create a new balance model
                invoice = Balance.objects.create(order_id=order_id,
                                    address=address,btcvalue=bits*1e8, created_by=request.user, balance=0)
                invoice_id = invoice.id
            details = self.track_balance(invoice_id)
            return Response(
                {
                    'addr': details['addr'],
                    'username': request.user.username,
                },
                status=status.HTTP_201_CREATED
            )

        else:
            print(r.status_code, r.text)
            return Response({'message': 'Error creating invoice'}, status=status.HTTP_400_BAD_REQUEST)
    
    def track_balance(self, pk):
        invoice_id = pk
        invoice = Balance.objects.get(id=invoice_id)
        data = {
                'order_id':invoice.order_id,
                'value':invoice.balance,
                'addr': invoice.address,
            }
        return data

class BuyView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated] 
    
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
class CoinbaseWebhookView(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        if request.method == 'GET':
            txid = request.GET.get('txid')
            value = float(request.GET.get('value'))
            status = request.GET.get('status')
            addr = request.GET.get('addr')

            invoice = Balance.objects.get(address=addr)
            
            if int(status) == 2:
                invoice.received = value
                invoice.txid = txid
                invoice.save()

                # update user's balance
                received = float(invoice.received)
                url = "https://www.blockonomics.co/api/price?currency=USD"
                response = requests.get(url)
                if response.text:
                    response_json = response.json()
                    usdvalue = received / 1e8 * response_json["price"]
                else:
                    # Handle the case where the response is empty
                    return Response({'message': 'Error: Received an empty response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                invoice.balance += usdvalue
                invoice.save()
                update_user_2(invoice.created_by.username,invoice.created_by.email,usdvalue)
                update_admins(usdvalue)

            return Response({'message': 'Balance updated'},status=200)
        elif int(status) == 0:
            received = float(invoice.received)
            usdvalue = received / 1e8 * response["price"]
            update_user(invoice.created_by.username,invoice.created_by.email,usdvalue)
            return Response({'message': 'Balance update started'},status=200)
        elif int(status) == 1:
            received = float(invoice.received)
            usdvalue = received / 1e8 * response["price"]
            update_user(invoice.created_by.username,invoice.created_by.email,usdvalue)
            return Response({'message': 'Balance update partial'},status=200)
        else:
            received = float(invoice.received)
            usdvalue = received / 1e8 * response["price"]
            update_user_3(invoice.created_by.username,invoice.created_by.email,usdvalue)
            return Response({'message': 'Balance update failed'},status=400)