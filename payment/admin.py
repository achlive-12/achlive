from django.contrib import admin
from .models import *
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('status','product', 'order_id', 'address', 'btcvalue', 'received', 'sold', 'created_by','created_at')
    list_filter = ('sold',"received")
    search_fields = ('created_by','order_id')
    
    list_editable = ('sold','created_at','product')

    fieldsets = (
        (None, {
            'fields': ('status', 'order_id', 'address', 'btcvalue', 'received', 'product', 'created_by','created_at')
        }),
    )
admin.site.register(Invoice, InvoiceAdmin)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ( 'order_id', 'address', 'balance', 'received', 'created_by','created_at')
    
    search_fields = ('created_by__user_name',)
    
    list_editable = ('balance',)

    fieldsets = (
        (None, {
            'fields': ( 'order_id', 'address', 'received', 'balance', 'created_by','created_at')
        }),
    )
admin.site.register(Balance, BalanceAdmin)

class Telegram_ClientAdmin(admin.ModelAdmin):
    list_display = ( 'order_id', 'address', 'balance', 'received', 'chat_id','created_at')
    
    search_fields = ('chat_id',)
    
    list_editable = ('balance',)

    fieldsets = (
        (None, {
            'fields': ( 'order_id', 'address', 'received', 'balance', 'chat_id',)
        }),
    )
admin.site.register(Telegram_Client, Telegram_ClientAdmin)

class Telegram_Otp_botAdmin(admin.ModelAdmin):
    list_display = ( 'order_id', 'address', 'name', 'log', 'chat_id','created_at','number')
    
    search_fields = ('chat_id',)
    
    list_editable = ('balance',)

    fieldsets = (
        (None, {
            'fields': ( 'order_id', 'address', 'received', 'balance', 'chat_id',)
        }),
    )
admin.site.register(Telegram_Otp_bot, Telegram_Otp_botAdmin)