from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name="index"),
    path('login/',views.login,name="login"),
    path('register/',views.register,name='register'),
    path('register_post/',views.register_post,name='register_post'),
    path('login_post/',views.login_post,name='login_post'),

    # profile
    path('profile/', views.profile, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),

    path('about/',views.about,name='about'),
    path('contact/',views.contact, name='contact'),


    # dashboard
    path('dashboard_both/',views.dashboard_both,name='dashboard_both'),
    # product side
    path('product_list/',views.product_list,name='product_list'),
    path('lender/product/<int:id>/', views.single_product, name='single_product'),

    # product
    path('product_upload/',views.product_upload,name="product_upload"),
    path('product_upload_post/',views.product_upload_post,name="product_upload_post"),
    path('product_edit/<int:id>/', views.product_edit_post, name='product_edit'),
    path('product_edit_post/<int:id>/', views.product_edit_post, name='product_edit_post'),
    path('product_delete/<int:id>/', views.product_delete, name='product_delete'),
    



    # main product views
    path('all_products/',views.all_products,name='all_products'),
    path('search/', views.search_product, name='search_product'),
    path('product/',views.product,name='product'),
    path('product/<int:id>/', views.product_single, name='product_single'),
    path('contact_lender/<int:product_id>/', views.contact_lender, name='contact_lender'),

    # request
    path('product/<int:product_id>/book/', views.renter_request, name='renter_request'),
    path('rent_request/<int:request_id>/<str:action>/', views.update_rent_request_status, name='update_rent_request_status'),
    path('request_view_lender/', views.request_view_lender, name='request_view_lender'),
    path('request_view_lender/', views.request_view_lender, name='request_view_lender'),
    path('request_view_lender/<int:request_id>/', views.request_view_lender, name='request_view_lender_detail'),
    path('approve_request/<int:req_id>/', views.approve_request, name='approve_request'),
    path('reject_request/<int:req_id>/', views.reject_request, name='reject_request'),
    path('payment/<request_id>/', views.payment, name="payment"),
    path('payment_post/', views.payment_post, name="payment_post"),

    # payment
    path('proceed_payment/<int:request_id>/', views.proceed_to_payment, name='proceed_to_payment'),
    # path('confirm_payment/<int:request_id>/', views.confirm_payment, name='confirm_payment'),
]