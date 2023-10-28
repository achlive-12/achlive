from rest_framework import serializers
from .models import Balance, Invoice

class BalanceSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    class Meta:
        model = Balance
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    class Meta:
        model = Invoice
        fields = '__all__'