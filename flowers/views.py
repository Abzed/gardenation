from django.contrib.messages.constants import SUCCESS
from django.forms.models import modelformset_factory
from django.http.response import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.urls import reverse
from django.conf import settings
from django.db.models import Q
from .models import *
from .forms import *
from django.contrib.messages import constants as messages
from django.contrib import messages
import re
from django.utils.translation import ugettext as _
from django.contrib.auth.hashers import check_password
from .tokens import account_activation_token
from django.db.models import Max
    
User = settings.AUTH_USER_MODEL


def index(request, uuid=None):
    products = Product.objects.all().order_by('-date')
    p_id = Product.objects.filter(uuid=uuid)
    category = Category.objects.all()
    wishlist = Wishlist.objects.filter(wished_item__in=Product.objects.all())
    latest = Product.objects.all().order_by('-date')[0:4]
    popular = Product.objects.all().order_by('-view')[0:4]
    
    wedding = Product.objects.filter(category__category__contains='Wedding').all().count()
    funeral = Product.objects.filter(category__category__contains='Sympathy and Funeral').all().count()
    date = Product.objects.filter(category__category__contains='Date').all().count()
    mother = Product.objects.filter(category__category__contains="Mother's Day").all().count()
    thanks = Product.objects.filter(category__category__contains='Thank You').all().count()
    valentine = Product.objects.filter(category__category__contains='Valentines').all().count()
    birthday = Product.objects.filter(category__category__contains='Birthday').all().count()
    holiday = Product.objects.filter(category__category__contains='Holidays').all().count()
    
    return render(request, 'index.html', {'products': products, 'category': category, 
    'wishlist':wishlist, 'latest': latest, 'popular': popular, 'wedding': wedding, 'funeral': funeral, 
    'date': date, 'mother': mother, 'thanks': thanks, 'valentine': valentine, 
    'birthday': birthday, 'holiday': holiday})

def singleproduct(request, uuid):
    category = Category.objects.all()
    
    product = Product.objects.get(uuid=uuid)
    images = ProductImage.objects.filter(product=product)[0:6]
    product.view = product.view+1
    product.save()
    ave = Product.ave_rating(product)
    rating = Product.no_of_rating(product)
    count = Product.count_rating(product)
    reviews = Review.objects.filter(product=product).order_by('-date')
    
    one = Review.objects.filter(product=product).filter(rating__contains=1).count()
    two = Review.objects.filter(product=product).filter(rating__contains=2).count()
    three = Review.objects.filter(product=product).filter(rating__contains=3).count()
    four = Review.objects.filter(product=product).filter(rating__contains=4).count()
    five = Review.objects.filter(product=product).filter(rating__contains=5).count()
    
    user = product.user
    user_products = Product.objects.filter(user=user)
    product__title = product.title.split()
    
    q = Q()
    for word in product__title:
        q = Q(title__icontains = word)
        related = Product.objects.filter(q)
    
    return render(request, './products/singleproduct.html', {'product': product, 'rating': rating, 'reviews': reviews,
    'user_products': user_products, 'related': related, 'count': count, 'ave': ave, 'images': images, 'one': one, 
    'two': two, 'three': three, 'four': four, 'five': five, 'category': category}) 

def related(request, title):
    related = Product.objects.filter(Q(title__icontains=title))        
    return render(request, './products/singleproduct.html', {'related': related})


def all_reviews(request, uuid):
    category = Category.objects.all()
    
    product = Product.objects.get(uuid=uuid)
    reviews = Review.objects.filter(product=product).order_by('-date')
    
    return render(request, './products/all_reviews.html', {'product': product, 'reviews': reviews, 'category': category}) 



def browse(request):
    products = Product.objects.all()
    category = Category.objects.all()
    
    
    paginate_by = request.GET.get('paginate', 8) or 8
    
    paginator = Paginator(products, paginate_by)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    return render(request, './products/browse.html', {'products': products, 'category': category, 
     'page_obj': page_obj, 'paginate_by': paginate_by})


def category_filter(request, category):
    products = Product.objects.filter(category__category=category)
    query = "Category"
    category = Category.objects.all()
    
    
    paginate_by = request.GET.get('paginate', 8) or 8
    
    paginator = Paginator(products, paginate_by)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    return render(request, './products/browse.html', {'products': products, 'category': category, 
    'page_obj': page_obj, 'query': query})




def price_filter(request):    
    if request.GET.get("max") == '':
        highest = Product.objects.all().aggregate(Max('price')).get('price__max')
        min_price = request.GET.get("min")     
        products = Product.objects.filter(price__range=[min_price, highest])
        
    elif request.GET.get("min") == '':
        lowest = 0   
        max_price = request.GET.get("max")     
        products = Product.objects.filter(price__range=[lowest, max_price])
        
    else:
        min_price = request.GET.get("min")
        max_price = request.GET.get("max")
        products = Product.objects.filter(price__range=[min_price, max_price])
        
    category = Category.objects.all()
    
    
    paginate_by = request.GET.get('paginate', 16) or 16
    
    paginator = Paginator(products, paginate_by)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    return render(request, './products/search.html', {'products': products, 'category': category,
    'page_obj': page_obj})

def order_by_latest(request):
    category = Category.objects.all()
    products = Product.objects.order_by('-date')
    
    
    paginate_by = request.GET.get('paginate', 8) or 8
    
    paginator = Paginator(products, paginate_by)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    return render(request, './products/browse.html', {'products': products, 'category': category, 
    'page_obj': page_obj})

def order_by_last(request):
    category = Category.objects.all()
    products = Product.objects.order_by('date')
    
    
    paginate_by = request.GET.get('paginate', 8) or 8
    
    paginator = Paginator(products, paginate_by)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    return render(request, './products/browse.html', {'products': products, 'category': category,
    'page_obj': page_obj})

def random(request):
    category = Category.objects.all()
    products = Product.objects.all().order_by('?')
    
    
    paginate_by = request.GET.get('paginate', 8) or 8
    
    paginator = Paginator(products, paginate_by)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    return render(request, './products/browse.html', {'products': products, 'category': category,
    'page_obj': page_obj})


def search_products(request):
    search_prod = request.GET.get("product")
    search_loc = request.GET.get("location")
    search_cat = request.GET.get("category")
    products = Product.objects.filter(Q(title__icontains=search_prod), Q(location__icontains=search_loc), Q(category__category__icontains=search_cat))
    
    message_prod = f"{search_prod}"
    message_loc = f"{search_loc}"
    message_cat = f"{search_cat}"
    
    category = Category.objects.all()
    
    
    paginate_by = request.GET.get('paginate', 16) or 16
    
    paginator = Paginator(products, paginate_by)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    return render(request, './products/search.html', {'products': products, 'category': category, 
    'page_obj': page_obj,  'mesage_prod': message_prod, 'message_loc': message_loc, 'message_cat': message_cat,})
        
    # return render(request, './products/search.html', {'products': products, 'mesage_prod': message_prod, 'message_loc': message_loc, 'message_cat': message_cat, 'category': category})

def search_title(request):
    title = request.GET.get("autoComplete")
    products = Product.objects.filter(Q(title__icontains=title))
    
    query = str(title)
    
    message_prod = f"{title}"
        
    category = Category.objects.all()
    
    
    paginate_by = request.GET.get('paginate', 16)
    
    paginator = Paginator(products, paginate_by)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    return render(request, './products/search.html', {'products': products, 'category': category,
    'page_obj': page_obj,  'mesage_prod': message_prod, 'query': query})

def search_location(request):
    location = request.GET.get("autoComplete2")
    products = Product.objects.filter(Q(location__icontains=location))
    
    message_loc = f"{location}"
        
    category = Category.objects.all()
    
    
    paginate_by = request.GET.get('paginate', 16) or 16
    
    paginator = Paginator(products, paginate_by)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    return render(request, './products/search.html', {'products': products, 'category': category,
    'page_obj': page_obj,  'message_loc': message_loc,})

def search_view(request):
    term = request.GET.get('autoComplete')
    data = []
    if term:
        items = Product.objects.filter(title__icontains=term)
        for item in items:
         data.append(item.title)

    return JsonResponse({'status': 200, 'data': data})  

def search_view2(request):
    term = request.GET.get('autoComplete2')
    data = []
    if term:
        items = Product.objects.filter(location__icontains=term)
        for item in items:
         data.append(item.location)

    return JsonResponse({'status': 200, 'data': data})  




@login_required
def buyerprofile(request, username):
        
    user = get_object_or_404(CustomUser, username=username)
    
    profile = Buyer.objects.get(buyer=user)
    return render(request,'./profiles/buyerprofile/profile.html', {'profile': profile})

@login_required
def buyerprofile_update(request, username):
    
    user = get_object_or_404(CustomUser, username=username)
    
    if request.method == 'POST':
        name = request.POST["username"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        phone_number = request.POST["phone_number"]        
        
        user.username = name
        user.last_name = last_name
        user.email = email
        user.phone_number = phone_number
        user.save()
        
        if 'avatar' in request.FILES:
            avatar = request.FILES['avatar']
            user.avatar = avatar
            user.save()
            
        return redirect('buyerprofile', username=user.username) 

    profile = Buyer.objects.get(buyer=user)

    return render(request,'./profiles/buyerprofile/profile.html', {'profile': profile})
 
@login_required   
def wishlist(request, username):
    user = get_object_or_404(CustomUser, username=username)
    profile = Buyer.objects.get(buyer=user)
    wishlist = Wishlist.objects.filter(user=user)
    return render(request,'./profiles/buyerprofile/wishlist.html', {'wishlist': wishlist})



from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def rate(request, uuid):
    product = Product.objects.get(uuid=uuid)
    form = ReviewForm(request.POST)
    if request.method == "POST":        
        if form.is_valid():
            title = form.cleaned_data.get("title")
            rating = form.cleaned_data.get("rating")
            description = form.cleaned_data.get("description")
            purchased = form.cleaned_data.get("purchased")
            review = Review.objects.create(title=title, description=description, user=request.user, rating=rating, purchased=purchased, product=product)
            print(review)
            return HttpResponseRedirect(reverse('singleproduct', args=[uuid]))
        else:
            form = ReviewForm()

    return render(request,'./products/review.html', {'product': product, 'form': form})
@login_required
def add_wishlist(request):
    product_uuid = request.GET['product_id']
    product = Product.objects.get(uuid=product_uuid)
    data={}
    mylist = Wishlist.objects.filter(user = request.user, wished_item = product)
    
    if mylist.exists():
        mylist.delete()
        data = {'bool': True}
        messages.info(request, 'Product removed from wishlist')
    else:
        wishlist = Wishlist.objects.create(user = request.user, wished_item = product)
        messages.info(request, 'Product added to wishlist')
        data = {'bool': False}
    
    return JsonResponse(data)



def saved(request):
    product_uuid = request.GET['saving_id']
    product = Product.objects.get(uuid=product_uuid)
    data={}
    saved = Product.objects.filter(uuid = product_uuid)
    
    if saved.exists():
        saved.delete()
        data = {'bool': True}
        messages.info(request, 'Product removed from wishlist')
    else:
        wishlist = Wishlist.objects.create(user = request.user, wished_item = product)
        messages.info(request, 'Product added to wishlist')
        data = {'bool': False}
    
    return JsonResponse(data)



@login_required
def sellerprofile(request, username):
    user = get_object_or_404(CustomUser, username=username)
    profile = Seller.objects.get(seller=user)
    return render(request,'./profiles/sellerprofile/profile.html', {'profile': profile})

@login_required
def search_profile(request, first_name):
    search_profile = request.GET.get("search_profile")
    user = get_object_or_404(Seller, seller__first_name=first_name)
    products = Product.objects.filter(Q(title__icontains=search_profile))
    return render(request, './profiles/sellerprofile/search.html', {'products': products, 'user': user})

@login_required
def sellerprofile_update(request, username):
    
    user = get_object_or_404(CustomUser, username=username)
    
    seller = get_object_or_404(Seller, seller=user)
    
    if request.method == 'POST':
        name = request.POST["username"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        phone_number = request.POST["phone_number"]
        business_name = request.POST["business_name"]
        location = request.POST["location"]
        
        seller.business_name = business_name
        seller.location = location
        seller.save()
        
        
        user.username = name
        user.last_name = last_name
        user.email = email
        user.phone_number = phone_number
        user.save()
        
        if 'avatar' in request.FILES:
            avatar = request.FILES['avatar']
            user.avatar = avatar
            user.save()        
            
        return redirect('sellerprofile', username=user.username) 

    profile = Seller.objects.get(seller=user)

    return render(request,'./profiles/sellerprofile/profile.html', {'profile': profile})

def dashboard(request, username):
    products = Product.objects.filter(user__seller__username=username).order_by('-view')
    submitted = Product.objects.filter(user__seller__username=username).count()
    seller = get_object_or_404(Seller, seller__username=username)
    rating = Seller.user_rating(seller)
    saved = Wishlist.objects.filter(user__username=username)
    return render(request, './profiles/sellerprofile/dashboard.html', {'products': products, 'rating': rating, 'saved': saved, 'submitted': submitted, 'submitted': submitted})

def search_dashfilter(request, username):
    title = request.GET.get("dashfilter")
    products = Product.objects.filter(user__seller__username=username).filter(Q(title__icontains=title) | Q(sub_category__subcategory__icontains=title) | Q(category__category__icontains=title))
    seller = get_object_or_404(Seller, seller__username=username)
    rating = Seller.user_rating(seller)
    saved = Wishlist.objects.filter(user__username=username)
    submitted = Product.objects.filter(user__seller__username=username).count()
    return render(request, './profiles/sellerprofile/dashboard.html', {'products': products, 'rating': rating, 'saved': saved, 'submitted': submitted})

def dashsort_latest(request, username):
    products = Product.objects.filter(user__seller__username=username).order_by('-date')
    seller = get_object_or_404(Seller, seller__username=username)
    rating = Seller.user_rating(seller)
    saved = Wishlist.objects.filter(user__username=username)
    submitted = Product.objects.filter(user__seller__username=username).count()
    return render(request, './profiles/sellerprofile/dashboard.html', {'products': products, 'rating': rating, 'saved': saved, 'submitted': submitted})

def dashsort_oldest(request, username):
    products = Product.objects.filter(user__seller__username=username).order_by('date')
    seller = get_object_or_404(Seller, seller__username=username)
    rating = Seller.user_rating(seller)
    saved = Wishlist.objects.filter(user__username=username)
    submitted = Product.objects.filter(user__seller__username=username).count()
    return render(request, './profiles/sellerprofile/dashboard.html', {'products': products, 'rating': rating, 'saved': saved, 'submitted': submitted})

def dash_ascending(request, username):
    products = Product.objects.filter(user__seller__username=username).order_by('title')
    seller = get_object_or_404(Seller, seller__username=username)
    rating = Seller.user_rating(seller)
    saved = Wishlist.objects.filter(user__username=username)
    submitted = Product.objects.filter(user__seller__username=username).count()
    return render(request, './profiles/sellerprofile/dashboard.html', {'products': products, 'rating': rating, 'saved': saved, 'submitted': submitted})

def dash_descending(request, username):
    products = Product.objects.filter(user__seller__username=username).order_by('-title')
    seller = get_object_or_404(Seller, seller__username=username)
    rating = Seller.user_rating(seller)
    saved = Wishlist.objects.filter(user__username=username)
    submitted = Product.objects.filter(user__seller__username=username).count()
    return render(request, './profiles/sellerprofile/dashboard.html', {'products': products, 'rating': rating, 'saved': saved, 'submitted': submitted})

def edit_product(request, uuid, username):
    product = Product.objects.get(uuid=uuid)
    # product_images = ProductImage.objects.filter(product=product)
    ImageFormset = modelformset_factory(ProductImage, fields=('other_images',), extra=5, max_num=6)
    user = get_object_or_404(Seller, seller__username=username)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    images_form = ImageFormset(request.POST or None, request.FILES or None, queryset=ProductImage.objects.filter(product=product))
    if request.method == "POST":
        if form.is_valid() and images_form.is_valid():           
            data = form.save(commit=False)
            data.user = user
            data.category = data.sub_category.category
            data.save()
            # image_data = images_form.save(commit=False) 
            # image_data.product = data
            # image_data.save()
            data_images = ProductImage.objects.filter(product=product)
            for index, img in enumerate(images_form):
                if img.cleaned_data:
                    if img.cleaned_data['id'] is None:
                        photos = ProductImage(product=data, other_images=img.cleaned_data.get('other_images'))
                        photos.save()
                        
                    else:
                        photos = ProductImage(product=data, other_images=img.cleaned_data.get('other_images'))
                        d = ProductImage.objects.get(id=data_images[index].id)
                        d.other_images = photos.other_images
                        d.save()
            return HttpResponseRedirect(reverse('posted', args=[username]))
        else:
            form = ProductForm(instance=product)
            images_form = ImageFormset(queryset=ProductImage.objects.filter(product=product))
    return render(request, './profiles/sellerprofile/editproduct.html', {'form': form, 'images_form': images_form})

def delete_product(request, uuid):
    product = Product.objects.get(uuid=uuid)
    try:
        product.delete()
        messages.add_message(request, messages.INFO, "Product removed from wishlist")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))  

    except:
        messages.add_message(request, messages.ERROR, "There was a problem deleting the product!")
    return HttpResponse('Deleted')

def delete_wishitem(request, uuid):
    saved_item = Wishlist.objects.get(wished_item__uuid=uuid)
    try:
        saved_item.delete()
        messages.add_message(request, messages.INFO, "Item removed from wishlist")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))  

    except:
        messages.add_message(request, messages.ERROR, "There was a problem deleting the product!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 
    


@login_required
def posted(request, username):
    product = Product.objects.filter(user__seller__username=username).order_by('-date')
        
    paginator = Paginator(product, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'./profiles/sellerprofile/posted.html', {'page_obj': page_obj})


def search_postedfilter(request, username):
    title = request.GET.get("postedfilter")
    product = Product.objects.filter(user__seller__username=username).filter(Q(title__icontains=title) | Q(sub_category__subcategory__icontains=title) | Q(category__category__icontains=title))
    
    paginator = Paginator(product, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'./profiles/sellerprofile/posted.html', {'page_obj': page_obj})

def posted_latest(request, username):
    product = Product.objects.filter(user__seller__username=username).order_by('-date')
    
    paginator = Paginator(product, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'./profiles/sellerprofile/posted.html', {'page_obj': page_obj})

def posted_oldest(request, username):
    product = Product.objects.filter(user__seller__username=username).order_by('date')
    
    paginator = Paginator(product, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'./profiles/sellerprofile/posted.html', {'page_obj': page_obj})

def posted_ascending(request, username):
    product = Product.objects.filter(user__seller__username=username).order_by('title')
    
    paginator = Paginator(product, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'./profiles/sellerprofile/posted.html', {'page_obj': page_obj})

def posted_descending(request, username):
    product = Product.objects.filter(user__seller__username=username).order_by('-title')
    
    paginator = Paginator(product, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'./profiles/sellerprofile/posted.html', {'page_obj': page_obj})


@login_required
def saved(request, username):
    user = get_object_or_404(CustomUser, username=username)
    wishlist = Wishlist.objects.filter(user=user)
    
    paginator = Paginator(wishlist, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'./profiles/sellerprofile/saved.html', {'page_obj': page_obj})

def search_saved(request, username):
    title = request.GET.get("savedfilter")
    
    user = get_object_or_404(CustomUser, username=username)
    wishlist = Wishlist.objects.filter(user=user).filter(Q(wished_item__title__icontains=title) | Q(wished_item__sub_category__subcategory__icontains=title) | Q(wished_item__category__category__icontains=title))
    
    paginator = Paginator(wishlist, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'./profiles/sellerprofile/saved.html', {'page_obj': page_obj})

def latest_saved(request, username):
    user = get_object_or_404(CustomUser, username=username)
    wishlist = Wishlist.objects.filter(user=user).order_by('-wished_item__date')
    
    paginator = Paginator(wishlist, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'./profiles/sellerprofile/saved.html', {'page_obj': page_obj})

def oldest_saved(request, username):
    user = get_object_or_404(CustomUser, username=username)
    wishlist = Wishlist.objects.filter(user=user).order_by('wished_item__date')
    
    paginator = Paginator(wishlist, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'./profiles/sellerprofile/saved.html', {'page_obj': page_obj})

def ascending_saved(request, username):
    user = get_object_or_404(CustomUser, username=username)
    wishlist = Wishlist.objects.filter(user=user).order_by('wished_item__title')
    
    paginator = Paginator(wishlist, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'./profiles/sellerprofile/saved.html', {'page_obj': page_obj})

def descending_saved(request, username):
    user = get_object_or_404(CustomUser, username=username)
    wishlist = Wishlist.objects.filter(user=user).order_by('-wished_item__title')
    
    paginator = Paginator(wishlist, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'./profiles/sellerprofile/saved.html', {'page_obj': page_obj})



@login_required
def add(request, username):
    all_category = Category.objects.all()
    user = get_object_or_404(Seller, seller__username=username)
    if request.method == 'POST':
        title = request.POST["title"]
        price = request.POST["price"]
        location = request.POST.get("location", user.location) 
        images = request.FILES.getlist('images')
        phone_number = request.POST.get("phone_number", user.seller.phone_number)
        category = request.POST["category"]
        
        cat = Category.objects.get(category=category)
                
        for image in images: 
            img = image    
                   
        product = Product.objects.create(user=user, title=title, images=img, price=price, category=cat, location=location)
        
        cumstomuser = CustomUser.objects.filter(username=username).update(phone_number=phone_number)
                   
        for img in images: 
            productimages = ProductImage()
            productimages.product = product
            productimages.other_images = img
            productimages.save()
                        
        return HttpResponseRedirect(reverse('posted', args=[username]))
    
    return render(request,'./profiles/sellerprofile/add.html', {'user': user, 'category': all_category})


def registration_type(request):
    return render(request, './authentication/registration_type.html',)


def sellersignup(request):
    django_logout(request)
    if request.method == 'POST':
        username = request.POST["username"]
        last_name = request.POST["last_name"]
        business_name = request.POST["business_name"]
        email = request.POST["email"]
        phone_number = request.POST["phone_number"]
        password = request.POST["password1"]
        password_confirmation = request.POST["password2"]
        
        min_length = 8
        
        if len(password) < min_length:
            messages.info(request, "The password must be at least %d characters long." % min_length)
            return redirect('sellersignup')

        # At least one letter and one non-letter
        elif not re.findall('\d', password):
            messages.info(request, "The password must contain at least one letter and at least one digit or" \
            " punctuation character.")
            return redirect('sellersignup')
            
        elif not re.findall('[A-Z]', password):
            messages.info(request, "The password must contain at least an UPPERCASE letter and at least one digit or" \
            " punctuation character.")
            return redirect('sellersignup')
        
        
        # user = CustomUser.objects.create(username=username, last_name=last_name, email=email, phone_number=phone_number, 
        # gender=gender, password=password, password1=password1, is_buyer=True)          
        
        if password == password_confirmation:  
            if CustomUser.objects.filter(email = email).exists():                    
                messages.info(request,'Email already exists')
                return redirect('sellersignup')
            elif CustomUser.objects.filter(username = username).exists():
                messages.info(request,'A user with that name already exists')
                return redirect('sellersignup')
            else:
                user = CustomUser(username=username, last_name=last_name, email=email, phone_number=phone_number,
                 is_seller=True, is_active=True)
                
                user.set_password(password)
                user.save()
                seller = Seller(seller=user, business_name=business_name)
                seller.save()

                login(request, user)
                return HttpResponseRedirect('/')

                # login(request, user)
                # return redirect('/')
                # return redirect('login')
        else:
            messages.info(request,'Passwords do not match')
            return redirect('sellersignup')
    return render(request, './authentication/seller/signup.html')


def buyersignup(request):
    django_logout(request)
    if request.method == 'POST':
        username = request.POST["username"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        phone_number = request.POST["phone_number"]
        gender = request.POST.get('gender', 'N/A')
        password = request.POST["password1"]
        password_confirmation = request.POST["password2"]
        # validate_password(password)
        
        min_length = 8
        
        if len(password) < min_length:
            messages.info(request, "The password must be at least %d characters long." % min_length)
            return redirect('buyersignup')

        # At least one letter and one non-letter
        elif not re.findall('\d', password):
            messages.info(request, "The password must contain at least one letter and at least one digit or" \
            " punctuation character.")
            return redirect('buyersignup')
            
        elif not re.findall('[A-Z]', password):
            messages.info(request, "The password must contain at least an UPPERCASE letter and at least one digit or" \
            " punctuation character.")
            return redirect('buyersignup')
        
        
        # user = CustomUser.objects.create(username=username, last_name=last_name, email=email, phone_number=phone_number, 
        # gender=gender, password=password, password1=password1, is_buyer=True)          
        
        if password == password_confirmation:  
            if CustomUser.objects.filter(email = email).exists():                    
                messages.info(request,'Email already exists')
                return redirect('buyersignup')
            elif CustomUser.objects.filter(username = username).exists():
                messages.info(request,'A user with that name already exists')
                return redirect('buyersignup')
            else:
                user = CustomUser(username=username, last_name=last_name, email=email, phone_number=phone_number,
                 is_buyer=True, is_active=True)
                
                user.set_password(password)
                user.save()
                
                buyer = Buyer.objects.create(buyer=user)
                
                login(request, user)
                return HttpResponseRedirect('/')                

                # login(request, user)
                # return redirect('/')
                # return redirect('login')
        else:
            messages.info(request,'Passwords do not match')
            return redirect('buyersignup')
        
    return render(request, './authentication/buyer/signup.html')




def changepassword(request, username):
    user = get_object_or_404(CustomUser, username=username)
    profile = Buyer.objects.get(buyer=user)
    
    if request.method == 'POST':
        password = request.POST["password1"]
        password_confirmation = request.POST["password2"]
        oldpassword = request.POST["oldpassword"]
        
        if check_password(oldpassword, request.user.password):
            new_password = password
            confirm_password = password_confirmation
            
            min_length = 8
        
            if len(new_password) < min_length:
                messages.add_message(request, messages.ERROR, "The password must be at least %d characters long." % min_length)
                return redirect('buyerprofile', username=user.username)

            # At least one letter and one non-letter
            elif not re.findall('\d', new_password):
                messages.add_message(request, messages.ERROR, "The password must contain at least one letter and digit or" \
                " punctuation character.")
                return redirect('buyerprofile', username=user.username)
                
            elif not re.findall('[A-Z]', new_password):
                messages.add_message(request, messages.ERROR, "The password must contain at least an UPPERCASE letter and at least one digit or" \
                " punctuation character.")
                return redirect('buyerprofile', username=user.username)
    
            elif new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                
                update_session_auth_hash(request, user) # <-- This code will keep session when user change password
                
                messages.add_message(request, messages.SUCCESS, 'Password changed successfully.')
                return redirect('buyerprofile', username=user.username) 
            else:
                messages.add_message(request, messages.ERROR, 'Passwords do not match!')
                

        else: 
            messages.add_message(request, messages.ERROR, 'Invalid password.')

    return render(request,'./profiles/buyerprofile/profile.html', {'profile': profile})

def changesellerpassword(request, username):
    user = get_object_or_404(CustomUser, username=username)
    profile = Seller.objects.get(seller=user)
    
    if request.method == 'POST':
        password = request.POST["password1"]
        password_confirmation = request.POST["password2"]
        oldpassword = request.POST["oldpassword"]
        
        if check_password(oldpassword, request.user.password):
            new_password = password
            confirm_password = password_confirmation
            
            min_length = 8
        
            if len(new_password) < min_length:
                messages.add_message(request, messages.ERROR, "The password must be at least %d characters long." % min_length)
                return redirect('sellerprofile', username=user.username)

            # At least one letter and one non-letter
            elif not re.findall('\d', new_password):
                messages.add_message(request, messages.ERROR, "The password must contain at least one letter and digit or" \
                " punctuation character.")
                return redirect('sellerprofile', username=user.username)
                
            elif not re.findall('[A-Z]', new_password):
                messages.add_message(request, messages.ERROR, "The password must contain at least an UPPERCASE letter and at least one digit or" \
                " punctuation character.")
                return redirect('sellerprofile', username=user.username)
    
            elif new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                
                update_session_auth_hash(request, user) # <-- This code will keep session when user change password
                
                messages.add_message(request, messages.SUCCESS, 'Password changed successfully.')
                return redirect('sellerprofile', username=user.username) 
            else:
                messages.add_message(request, messages.ERROR, 'Passwords do not match!')
                

        else: 
            messages.add_message(request, messages.ERROR, 'Invalid password.')

    return render(request,'./profiles/sellerprofile/profile.html', {'profile': profile})
        
        


def signin(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        return HttpResponseRedirect('/')
    else:
        messages.add_message(request, messages.ERROR, 'Invalid email or password. Please try again.')

    return render(request, 'authentication/login.html', {'email': username})

@login_required
def logout(request):
    django_logout(request)
    return  HttpResponseRedirect('/')

@login_required
def delete_account(request, username):  
    user = get_object_or_404(CustomUser, username=username)
    profile = Buyer.objects.get(buyer=user)  
    try:
        user.delete()
        profile.delete()
        return redirect('index')

    except:
        messages.add_message(request, messages.ERROR, "There was a problem deleting your account!")    
        
    return render(request,'./profiles/buyerprofile/profile.html', {'profile': profile})

@login_required
def delete_seller_account(request, username):  
    user = get_object_or_404(CustomUser, username=username)
    profile = Seller.objects.get(seller=user)  
    try:
        user.delete()
        profile.delete()
        return redirect('index')

    except:
        messages.add_message(request, messages.ERROR, "There was a problem deleting your account!")    
        
    return render(request,'./profiles/sellerprofile/profile.html', {'profile': profile})





