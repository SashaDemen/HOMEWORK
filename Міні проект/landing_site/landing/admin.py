from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','name','email','phone','product','created_at')
    search_fields = ('name','email','phone','product','message')
    list_filter = ('created_at',)
    readonly_fields = ('created_at','ip','user_agent')
