import uuid
from cloudinary.models import CloudinaryField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg
from django.urls import reverse


class UserAccountManager(BaseUserManager):
    def create_user(self, email, username, last_name, password=None):
        if not email:
            raise ValueError('Email must be set!')
        user = self.model(email=email, username=username, last_name=last_name)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, last_name, password):
        user = self.create_user(email, username, last_name, password)
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save()
        return user
    
    def get_short_name(self):
        return self.username

    def get_full_name(self):
        return  self.username

    def has_perm(self, perm, ob=None):
        return True

    def has_module_perms(self, app_label):
        return True




class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=70, unique=True)    
    phone_number = models.CharField(max_length=19, null = True, blank = True)
    avatar = CloudinaryField('image')
    is_seller = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=False)
    last_name = models.CharField(_('last name'), max_length=50)
    email = models.EmailField(_('email address'), unique=True) 
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    
    ordering = ('email',)
    list_display = ('username', 'last_name', 'email', 'gender')
    
     
    
    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = []
    REQUIRED_FIELDS = ['email', 'last_name']
    
    objects = UserAccountManager()
    
    def get_short_name(self):
        return self.email

    def get_full_name(self):
        return  self.email

    def has_perm(self, perm, ob=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def natural_key(self):
        return self.email

  

class Seller(models.Model):
    seller = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    business_name = models.CharField(max_length=150)
    location = models.CharField(max_length=55, null=True, blank=True)

    def __str__(self):
        return self.seller.username
    
    def user_rating(self):
        review = Review.objects.filter(product__user__seller__username=self).aggregate(avarage=Avg('rating'))
        avg=0
        if review["avarage"] is not None:
            avg=float(review["avarage"])
        return avg
    

class Buyer(models.Model):
    buyer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.buyer.username
    

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.category


class Picture(models.Model):
    images = models.ImageField(upload_to='images/', blank=True, null=True,)

    def __str__(self):
        return self.id
    

class Product(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='seller_profile')
    title = models.CharField(max_length=200, null=True, blank=True)
    color = models.CharField(max_length=200, null=True, blank=True)
    images = CloudinaryField('image')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product_category', null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    price = models.IntegerField(default=0, null=True, blank=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    view = models.IntegerField(default=0)  
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('singleproduct', args=[str(self.uuid)])
    
    def save_image(self):
        self.save()
        
    # def product_date(self):
    #     expires = Product.date
    #     return expires
        
    @classmethod
    def search_products(cls,search_term):
        items = Product.objects.filter(product_name__icontains=search_term)
        return items
        
    def delete_image(self):
        self.delete()  
        
    def no_of_rating(self):
        review = Review.objects.filter(product=self).aggregate(avarage=Avg('rating'))
        avg=0
        if review["avarage"] is not None:
            avg=float(review["avarage"])
        return (avg*100)/5
    
    def ave_rating(self):
        review = Review.objects.filter(product=self).aggregate(avarage=Avg('rating'))
        avg=0
        if review["avarage"] is not None:
            avg=float(review["avarage"])
        return avg

    
    def count_rating(self):
        ratings = Review.objects.filter(product=self)
        # count = ratings.rating
        return len(ratings)
    
    def sub_categories(self):
        sub_cat = Product.objects.filter(sub_category=self)
        return sub_cat
    

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=None, blank=True, null=True)
    other_images = CloudinaryField('image')
    def __str__(self):
        return self.product.title
    
class Review(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    rating = models.IntegerField(default=0, validators= [MaxValueValidator(5), MinValueValidator(1)])
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_comment')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='post_comment')
    purchased = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return self.product.title
    

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_products')# here CASCADE is the behavior to adopt when the referenced object(because it is a foreign key) is deleted. it is not specific to django,this is an sql standard.
    wished_item = models.ForeignKey(Product,on_delete=models.CASCADE, related_name='saves')

    def __str__(self):
        return self.wished_item.title
    
    def delete(self):
        self.delete() 
    