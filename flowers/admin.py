from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin  as BaseUserAdmin

from .forms import SignUpForm

class UserAdmin(BaseUserAdmin):
    add_form =  SignUpForm
    
    list_display = ('email', 'username', 'phone_number', 'is_active', 'is_buyer',  'is_seller')
    list_filter = ('is_superuser',)

    fieldsets = (
        (None, {'fields': ('email', 'is_staff', 'is_superuser', 'password', 'is_buyer',  'is_seller', 'is_active')}),
        ('Personal info', {'fields': ('username', 'phone_number', 'avatar')}),
        ('Groups', {'fields': ('groups',)}),
        ('Permissions', {'fields': ('user_permissions',)}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'is_staff', 'is_buyer','is_seller', 'is_active', 'is_superuser', 'password1', 'password2')}),
        ('Personal info', {'fields': ('username', 'last_name', 'phone_number', 'avatar')}),
        ('Groups', {'fields': ('groups',)}),
        ('Permissions', {'fields': ('user_permissions',)}),
    )

    search_fields = ('email', 'username', 'phone_number')
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(CustomUser,UserAdmin)

class ProductImageAdmin(admin.StackedInline):
    model = ProductImage

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]
 
    class Meta:
       model = Product
 
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    pass


# admin.site.register(Product)
admin.site.register(Buyer)
admin.site.register(Seller)
admin.site.register(Review)
admin.site.register(Wishlist)
