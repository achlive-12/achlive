from rest_framework import serializers
from .models import Balance, Invoice
from store.serializers import ProductSerializer

class BalanceSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    class Meta:
        model = Balance
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    product = ProductSerializer()
    class Meta:
        model = Invoice
        fields = ['created_by','amount','product',]