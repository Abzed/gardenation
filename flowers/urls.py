from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    path('', views.index, name='index'),
    path('product/<str:uuid>', views.singleproduct, name='singleproduct'),
    path('product/<str:uuid>/rate-product', views.rate, name='review'),
    path('product/<str:uuid>/all-reviews', views.all_reviews, name='all_reviews'),       
    
      
    path('products/browse-all-products', views.browse, name='browse'),
    path('products/browse-all-products/random', views.random, name='random'),      
    path('products/category<str:category>', views.category_filter, name='category_filter'),     
    path('products/price-range', views.price_filter, name='price_filter'),    
    path('products/browse-all-products/latest', views.order_by_latest, name='order_by_latest'), 
    path('products/browse-all-products/oldest', views.order_by_last, name='order_by_last'),   
    
    
    path('products/search', views.search_products, name='search_products'),    
    path('products/autosearch', views.search_title, name='search_title'),
    path('products/location-autosearch', views.search_location, name='search_location'),
    
    
    path('search', views.search_view, name='search_view'),
    path('location-search', views.search_view2, name='search_view2'),
    path('add-to-wishlist', views.add_wishlist, name='add_wishlist'),
    
    
    path('profile/<str:username>', views.buyerprofile, name='buyerprofile'),
    path('profile/update/<str:username>', views.buyerprofile_update, name='buyerprofile_update'),
    path('profile/changepassword/<str:username>', views.changepassword, name='changepassword'),
    path('profile/delete-account/<str:username>', views.delete_account, name='delete_account'),
    path('profile/<str:username>/wishlist', views.wishlist, name='wishlist'),
    
    
    path('vendor-profile/<str:username>', views.sellerprofile, name='sellerprofile'),
    path('vendor-profile/<str:username>/add', views.add, name='add'),
    
    
    path('vendor-profile/<str:username>/saved-products', views.saved, name='saved'),
    path('vendor-profile/<str:username>/saved-products/search', views.search_saved, name='search_saved'),
    path('vendor-profile/<str:username>/saved-products/latest', views.latest_saved, name='latest_saved'),
    path('vendor-profile/<str:username>/saved-products/oldest', views.oldest_saved, name='oldest_saved'),
    path('vendor-profile/<str:username>/saved-products/ascending', views.ascending_saved, name='ascending_saved'),
    path('vendor-profile/<str:username>/saved-products/descending', views.descending_saved, name='descending_saved'),
    path('vendor-profile/<str:uuid>/remove', views.delete_wishitem, name='delete_wishitem'), 
    
    
    path('vendor-profile/<str:username>/my-products', views.posted, name='posted'),
    path('vendor-profile/<str:username>/my-products/search', views.search_postedfilter, name='search_postedfilter'),
    path('vendor-profile/<str:username>/my-products/latest', views.posted_latest, name='posted_latest'),
    path('vendor-profile/<str:username>/my-products/oldest', views.posted_oldest, name='posted_oldest'),
    path('vendor-profile/<str:username>/my-products/ascending', views.posted_ascending, name='posted_ascending'),
    path('vendor-profile/<str:username>/my-products/descending', views.posted_descending, name='posted_descending'),    
    
    
    path('vendor-profile/<str:username>/dashboard', views.dashboard, name='dashboard'),  
    path('vendor-profile/<str:username>/search_profile', views.search_profile, name='search_profile'),  
    path('vendor-profile/<str:username>/dashboard/filter_search', views.search_dashfilter, name='search_dashfilter'), 
    path('vendor-profile/<str:username>/dashboard/filter_by_latest', views.dashsort_latest, name='dashsort_latest'), 
    path('vendor-profile/<str:username>/dashboard/filter_by_oldest', views.dashsort_oldest, name='dashsort_oldest'), 
    path('vendor-profile/<str:username>/dashboard/filter_by_ascending', views.dash_ascending, name='dash_ascending'), 
    path('vendor-profile/<str:username>/dashboard/filter_by_descending', views.dash_descending, name='dash_descending'), 
    path('vendor-profile/<str:uuid>/<str:username>/edit_product', views.edit_product, name='edit_product'), 
    path('vendor-profile/<str:uuid>/delete_product', views.delete_product, name='delete_product'), 
     
    
    
    path('vendor-profile/<str:username>/changepassword', views.changesellerpassword, name='changesellerpassword'), 
    path('vendor-profile/<str:username>/sellerprofile_update', views.sellerprofile_update, name='sellerprofile_update'), 
    path('vendor-profile/<str:username>/delete-account', views.delete_seller_account, name='delete_seller_account'), 
    
    
    path('buyer-registration', views.buyersignup, name='buyersignup'),
    path('vendor-registration', views.sellersignup, name='sellersignup'),
    path('logout/', views.logout, name='logout'),
    path('account-type', views.registration_type, name='registration_type'),
    path('login', views.signin, name='login'),
    ] 

if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)