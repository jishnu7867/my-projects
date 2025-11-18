from django.urls import include,path
from ArtHome import views

urlpatterns = [
    path('index/',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('services/',views.services,name='services'),
    path('blog/',views.blog,name='blog'),
    path('contact/',views.contact,name='contact'),
    
    # path('home/', views.home, name='home'),
    path('login/',views.login,name='login'),
    path('login_post/',views.login_post,name='login_post'),
    path('seller_reg/', views.seller_reg, name='seller_reg'),
    path('seller_reg_post/', views.seller_reg_post, name='seller_reg_post'),
    path('buyer_reg/',views.buyer_reg,name='buyer_reg'),
    path('buyer_reg_post/',views.buyer_reg_post,name='buyer_reg_post'),
    path('login_category/', views.login_category, name='login_category'),


    path('dashboard/',views.dashboard,name='dashboard'),
    path('products/',views.products,name='products'),
    path('order_list/',views.order_list,name='order_list'),
    path('customers/',views.customers,name='customers'),
    path('reviews/',views.reviews,name='reviews'),
    path('earnings/',views.earnings,name='earnings'),
    path('settings/',views.settings,name='settings'),

    # seacrh
    path('search_products/',views.search_products,name='search_products'),
    path('search_order/',views.search_order,name='search_order'),


    path('seller_profile_page/',views.seller_profile_page,name='seller_profile_page'),
    path('seller_profile_edit/<id>/',views.seller_profile_edit,name='seller_profile_edit'),
    path('seller_profile_edit_post/',views.seller_profile_edit_post,name='seller_profile_edit_post'),
    path('seller_add_product/',views.seller_add_product,name='seller_add_product'),
    path('seller_add_product_post/',views.seller_add_product_post,name='seller_add_product_post'),
    # path('view_product/<int:id>/', views.view_product, name='view_product'),
    path('product_edit/<id>/',views.product_edit,name='product_edit'),
    path('product_edit_post/',views.product_edit_post,name='product_edit_post'),
    path('product_delete/<id>/',views.product_delete,name='product_delete'),
    # path('seller_product_view/', views.seller_product_view, name='seller_product_view'),


    # buyer
    path('product_list/',views.product_list,name="product_list"),
    path('profile_page/',views.profile_page,name='profile_page'),
    # path('buyer_home/',views.buyer_home,name='buyer_home'),
    path('buyer_profile_edit/<id>/',views.buyer_profile_edit,name='buyer_profile_edit'),
    path('buyer_profile_edit_post/',views.buyer_profile_edit_post,name='buyer_profile_edit_post'),
    # path('buyer_profile_delete/<id>/',views.buyer_profile_delete,name='buyer_profile_delete'),

    path("", views.index, name="index"),
    path("orders/", views.orders, name="orders"),
    path("review_post/", views.review_post, name="review_post"),
    path("product/<int:product_id>/", views.single_product, name="single_product"), 
   
    
    path('add_to_cart/<int:product_id>/',views.add_to_cart,name='add_to_cart'),
    path('view_cart/',views.view_cart,name='view_cart'),      
    path('remove_from_cart/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/',views.checkout,name='checkout'),
    path('place_order/',views.place_order,name='place_order'),
    path("payment/<int:order_id>/", views.payment, name="payment"),
    path('payment_post',views.payment_post,name='payment_post'),
    path('thankyou/',views.thankyou,name='thankyou'),
]