from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db.models import fields
from .models import *

class SignUpForm(UserCreationForm):    
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-lg', 'autocomplete':'off'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-lg', 'placeholder':'Last Name'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control email', 'placeholder':'Enter email'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control phone', 'placeholder':'Phone number'}), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control password', 'placeholder':'Enter password'}), required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control password', 'placeholder':'Confirm password'}), required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "last_name", "email", "phone_number")
        
    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )
        
class BuyerSignUpForm(forms.ModelForm):
        
    class Meta:
        model = Buyer
        exclude = ('buyer',)
        
class SellerSignUpForm(forms.ModelForm):
        
    class Meta:
        model = Seller
        fields = ("business_name", )
        
class ReviewForm(forms.ModelForm):
        
    class Meta:
        model = Review
        fields = ("title", "description", "rating", "purchased")
        
class ProductForm(forms.ModelForm):
        
    class Meta:
        model = Product
        exclude = ("user", "view", "date")
        
class ProductImageForm(forms.ModelForm):
    
    other_images = forms.ImageField(label="Add Additional Images", widget=forms.ClearableFileInput(attrs={'multiple': True}))  
        
    class Meta:
        model = ProductImage
        fields = ("other_images",)
    
        
        

        