from django.contrib import admin
from .models import Transaction
# Register your models here.

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'firebase_uid', 'type', 'category', 'amount', 'date')
    search_fields = ('user__username', 'category', 'type')
    list_filter = ('type', 'category', 'date')

admin.site.register(Transaction, TransactionAdmin)
