
import datetime
from decimal import Decimal
import hashlib
from django.utils.timezone import now
import random
import string
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import redirect, render,get_object_or_404
from django.db.models import Q,Count

from ArtHome.models import *




# Create your views here.

# def home(request):
#     return render(request, 'home.html')

# INDEIX
def index(request):
    products=Product.objects.all().order_by('-id')[:3]
    buyer=Buyer.objects.all()
    return render(request,'index.html',{'products':products},)



# LOGIN
def login(request):
    return render(request,'login.html')

def login_post(request):
    email_or_mobile=request.POST['email_or_mobile']
    password=request.POST['password']

    user=Login.objects.filter(Q(email=email_or_mobile) | Q(mobile=email_or_mobile)).first()
    if user:
        log=Login.objects.filter(Q(email=email_or_mobile) | Q(mobile=email_or_mobile)).first()
        salt=user.salt
        password=password+salt
        password=hashlib.md5(password.encode('utf-8')).hexdigest()
        
        if log.password==password:
            request.session['lid']=log.id
            request.session['type']=log.type
            if log.type=='Seller':
                return HttpResponse('''<script>alert("Login successfull");window.location="/dashboard/";</script>''')
            elif log.type=='Buyer':
                return HttpResponse('''<script>alert("Login successfull");window.location="/index/";</script>''')
            else:
                return HttpResponse('''<script>alert("Invalid login category");window.location="/login/";</script>''')
        else:
            return HttpResponse('''<script>alert("Invalid password");window.location="/login/";</script>''')
    else:
        return HttpResponse('''<script>alert("Invalid username or password");window.location="/login/";</script>''')

# About us
def about(request):
    return render(request,'about.html')

# Services
def services(request):
    return render(request,'services.html')

# blog
def blog(request):
    return render(request,'blog.html')
                
# contact
def contact(request):
    return render(request,'contact.html')

#category
def login_category(request):
    return render(request,'reg_category.html')  






# for Seller Reg
def seller_reg(request):
    log=Login.objects.all()
    return render(request,'seller_reg.html')

def seller_reg_post(request):
    if request.method == "POST":
        brand = request.POST['brand']
        owner = request.POST['owner']
        address = request.POST['address']
        email = request.POST['email']
        mobile = request.POST['mob']
        password = request.POST['password']

        if Seller.objects.filter(Q(email=email) | Q(mobile=mobile)).exists():
            return HttpResponse('''<script>alert("An account with this Email or mobile number already exists");window.location="/login/";</script>''')

        salt = ''.join(random.choices(string.ascii_letters, k=7))
        password_hashed = hashlib.md5((password + salt).encode('utf-8')).hexdigest()

        log = Login(email=email, mobile=mobile, password=password_hashed, salt=salt, type='Seller')
        log.save()

        reg = Seller(brand=brand, owner=owner, address=address,
                     email=email, mobile=mobile, password=password_hashed, login=log)
        reg.save()

        return HttpResponse(''' <script>alert("Registration Successful");window.location="/login/";</script>''')



# DASHBOARD

def dashboard(request):
    product=Product.objects.filter(login_id=request.session['lid']).order_by('-created_at')[:4]
    product_count=Product.objects.count()
    order_count=Order.objects.count()
    seller = Seller.objects.filter(login_id=request.session['lid']) 
    orders=Order.objects.filter(product__login_id=request.session['lid']).order_by('-created_at')[:3]
    return render(request,'dashboard.html',{'seller':seller,'orders':orders,'product':product,'product_count':product_count,'order_count':order_count})

# Dashboard products

def products(request):
     product_list=Product.objects.filter(login_id=request.session['lid']).order_by('-created_at')
     product_with_count=product_list.annotate(sell_count=Count("order_product",distinct=True))
     paginator=Paginator(product_list,4)
     page_number=request.GET.get('page')
     products=paginator.get_page(page_number)
    #  for pro in product_with_count:
    #       print(pro.title)
    #       print(pro.sell_count)
     return render(request,'products.html',{'products':products})

def search_products(request):
    if request.method=="POST":
        #   sort_by=request.POST['sort_by']
          search=request.POST['search']
          products=Product.objects.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(category__icontains=search) |
            Q(sub_category__icontains=search),
            product=Product.objects.filter(login_id=request.session['lid'])
          )

    # if sort_by=='Price_asc':
    #       products=products.order_by('price')
    # elif sort_by=='price_desc':
    #       products=products.order_by('-price')
               
    #       return render(request,'products.html',{'product':products})

# Dashboard orderlist
def order_list(request):
    # if check_is_buyer(request):
        # products=Product.objects.filter(login_id=request.session['lid'])
        orders=Order.objects.filter(product__login_id=request.session['lid']).order_by('-created_at')
        return render(request,'seller_orders.html',{'orders':orders,})

def search_order(request):
     if request.method=='POST':
          
          
          search=request.POST['search']
          orders=Order.objects.filter(
               Q(id=search)|
               Q(fname__icontains=search)|
               Q(lname__icontains=search)|
               Q(state__icontains=search)|
            #    Q(product__category__icontains=search)|
               Q(postal_code__icontains=search),
               product__login_id=request.session['lid']
          )

          
               
          return render(request,'seller_orders.html',{'orders':orders})


#Dashboard Customers 

def customers(request):
    seller = Seller.objects.filter(login_id=request.session['lid'])
    all_orders=Order.objects.all().order_by('-created_at')
    unique_customers={}
    for order in all_orders:
        if order.email not in unique_customers:
            unique_customers[order.email]=order
    orders= unique_customers.values()
    return render(request,'customers.html',{'orders':orders,'seller':seller})

def search_customer(request):
    if request.method=="POST":
        search=request.POST['search']
        all_orders=Order.objects.all().order_by('-created_at')
        unique_customers={}
        for order in all_orders:
            if order.email not in unique_customers:
                unique_customers[order.email]=order
        orders=unique_customers.values().filter()



# Dashboard review

def reviews(request):
     return render(request,'reviews.html')

def earnings(request):
     return render(request,'earnings.html')

# Dashboard settings 

def settings(request):
     seller=Seller.objects.filter(login_id=request.session['lid'])
     return render(request,'settings.html',{'seller':seller})





# Seller profile

def seller_profile_page(request):
    # if check_is_seller(request):
        seller = Seller.objects.filter(login_id=request.session['lid']).first()
        return render(request,'seller_profile.html',{'seller': seller})
    # else:
    #     type=request.session['type']
    #     return HttpResponse(f'''<script>alert("you are not seller ");window.location='/login/'</script>''')

def seller_profile_edit(request,id):
    if check_is_seller:
        seller=Seller.objects.get(id=id)
        return render(request,'seller_profile_edit.html',{'seller':seller})
    else:
        return HttpResponse(f'''<script>alert("you are not seller ");window.location='/login/'</script>''') 

def seller_profile_edit_post(request):
    if check_is_seller(request):
        seller = Seller.objects.filter(login_id=request.session['lid'])
        if request.method=="POST":
            owner=request.POST['owner']
            brand=request.POST['brand']
            address=request.POST['address']
            city=request.POST['city']
            state=request.POST['state']
            pincode=request.POST['pincode']
            bio=request.POST['bio']
            
            id=request.POST['id']

            seller=Seller.objects.get(id=id)

            seller.owner=request.POST['owner']
            seller.brand=request.POST['brand']
            seller.address=request.POST['address']
            seller.city=request.POST['city']
            seller.state=request.POST['state']
            seller.pincode=request.POST['pincode']
            seller.bio=request.POST['bio']
            

            seller.save()
            return HttpResponse('''<script>alert("Changes saved successfully");window.location='/settings/';</script>''')
    else:
        return HttpResponse('''<script>alert("you are not seller ");window.location='/login/'</script>''')  


def seller_p_image(request):
     if request.method=="POST":
        profile_picture=request.FILES.get('profile_picture')
        id=request.POST['id']

        seller=Seller.objects.get(id=id)
        if 'profile_picture' in request.FILES:
            seller.profile_picture = request.FILES.get('profile_picture')
        seller.save()
        return HttpResponse('''<script>alert("Changes saved successfully");window.location='/settings/';</script>''')





# Add product

def seller_add_product(request):
    # if check_is_seller(request):
        return render(request,'seller_add_product.html')
    # else:
    #     return HttpResponse('''<script>alert(" you are not seller ");window.location='/login/';</script>''')

    

def seller_add_product_post(request):
        if request.method=="POST":
            title=request.POST['title']
            category=request.POST['category']
            sub_category=request.POST['sub_category']
            description=request.POST['description']
            images=request.FILES['images']
            qty=request.POST['qty']
            dimensions=request.POST['dimensions']
            price=request.POST['price']

            login_id = request.session['lid']

            product=Product(title=title,category=category,sub_category=sub_category,description=description,images=images,qty=qty,dimensions=dimensions,price=price,login_id=login_id)
            product.save()

            return HttpResponse('''<script>alert("Product added");window.location="/products/";</script>''')

# def seller_product_view(request):
#     # if check_is_seller(request):
#         lid=request.session['lid']
#         seller = Product.objects.filter(login_id=request.session['lid'])
#         return render(request, 'seller_products.html', {'seller': seller})
    # else:
    #     return HttpResponse('''<script>alert(" you are not seller ");window.location='/buyer_items_list/';</script>''')



# def view_product(request, id):
#     # if check_is_seller(request):
#         seller = Product.objects.filter(login_id=request.session['lid'])
#         return render(request, 'products.html', {'seller': seller})
    # else:
    #     return HttpResponse('''<script>alert(" you are not seller ");window.location='/buyer_items_list/';</script>''')





def product_edit(request,id):
    # if check_is_seller(request):
        seller=Product.objects.get(id=id)
        return render(request,'product_data_edit.html',{'seller':seller})
    # else:
    #     return HttpResponse('''<script>alert(" you are not seller ");window.location='/login/';</script>''')


def product_edit_post(request):
    if request.method == "POST":
        title = request.POST['title']
        category = request.POST['category']
        sub_category = request.POST['sub_category']
        description = request.POST['description']
        qty = request.POST['qty']
        dimensions = request.POST['dimensions']
        price = request.POST['price']
        id = request.POST['id']
        login_id = request.session['lid']

        seller = Product.objects.get(id=id)
        seller.title = title
        seller.category = category
        seller.sub_category = sub_category
        seller.description = description
        if 'images' in request.FILES:
            seller.images = request.FILES['images']

        seller.qty = qty
        seller.dimensions = dimensions
        seller.price = price

        seller.save()

        return HttpResponse(f'''<script>alert("Data updated successfully");window.location="/products/";</script>''')

    
def product_delete(request,id):
    seller=Product.objects.get(id=id).delete()
    return HttpResponse('''<script>alert("Data Deleted successfully");window.location="/view_product/{id}/";</script>''')
               
            










# for buyer
def buyer_reg(request):
    log=Login.objects.all()
    return render(request,'buyer_reg.html')

def buyer_reg_post(request):
    fname = request.POST['fname']
    lname = request.POST['lname']
    email = request.POST['email']
    mobile = request.POST['mobile']
    password = request.POST['password']

    if Buyer.objects.filter(Q(email=email) | Q(mobile=mobile)).exists():
        return HttpResponse('''<script>alert("An account with this Email or mobile number already exists");window.location="/login/";</script>''')

    salt = ''.join(random.choices(string.ascii_letters, k=7))
    hashed_password = hashlib.md5((password + salt).encode('utf-8')).hexdigest()

    log = Login(email=email, mobile=mobile, password=hashed_password, salt=salt, type='Buyer')
    log.save()

    reg = Buyer(fname=fname, lname=lname, email=email, mobile=mobile, password=hashed_password, login=log)
    reg.save()

    return HttpResponse('''<script>alert("Registration Successful");window.location="/login/";</script>''')



# Shop 

def product_list(request):
    # if check_is_buyer(request):
        
        products=Product.objects.all()
        return render(request,'shop.html',{'products':products})
    # else:
    #     type=request.session['type']
    #     return HttpResponse(f'''<script>alert("you are not buyer ");window.location='/login/'</script>''')

def single_product(request,id):
    product=Product.objects.get(id=id)
    products=Product.objects.all().order_by('-id')[:3]
    reviews =product.reviews.all().order_by('-created_at')

    avg_rating= reviews.aggregate(Avg('rating'))['rating_avg']
    return render(request,'single_product.html',{'product':product,'products':products,'reviews':reviews,'avg_rating':avg_rating,})



# Buyer profile

def profile_page(request):
    # if check_is_buyer(request):
        buyer = Buyer.objects.filter(login_id=request.session['lid']).first()
        return render(request,'buyer_profile.html',{'buyer': buyer})
    # else:
    #     type=request.session['type']
    #     return HttpResponse(f'''<script>alert("you are not buyer ");window.location='/login/'</script>''')

def buyer_profile_edit(request,id):
    # if check_is_buyer:
        buyer=Buyer.objects.get(id=id)
        return render(request,'buyer_profile_edit.html',{'buyer':buyer})
    # else:
    #     return HttpResponse(f'''<script>alert("you are not buyer ");window.location='/login/'</script>''') 

def buyer_profile_edit_post(request):
    # if check_is_buyer(request):
        buyer = Buyer.objects.filter(login_id=request.session['lid'])
        if request.method=="POST":
            address=request.POST['address']
            city=request.POST['city']
            state=request.POST['state']
            p_image=request.FILES.get('p_image')
            id=request.POST['id']

            buyer=Buyer.objects.get(id=id)

            buyer.address=request.POST['address']
            buyer.city=request.POST['city']
            buyer.state=request.POST['state']
            buyer.pincode=request.POST['pincode']
            if 'p_image' in request.FILES:
                buyer.p_image = request.FILES.get('p_image')

            buyer.save()
            return HttpResponse('''<script>alert("Changes saved successfully");window.location='/profile_page/';</script>''')
    # else:
        # return HttpResponse('''<script>alert("you are not buyer ");window.location='/login/'</script>''')  
    






# Buyer orders

def orders(request):
    # if check_is_buyer(request):
        
        orders_list=Order.objects.filter(login_id=request.session['lid']).order_by('-created_at')
        paginator=Paginator(orders_list,6)
        page_number=request.GET.get('page')
        orders=paginator.get_page(page_number)
        return render(request,'orders.html',{'orders':orders,})
    # else:
    #     return HttpResponse('''<script>alert("you are not buyer ");window.location='/login/'</script>''')


# Review
def review_post(request):
    if request.method=="POST":
        product_id=request.POST['product_id']
        order_id = request.POST['order_id']
        rating = request.POST['rating']
        comment = request.POST['comment']

        product = get_object_or_404(Product, id=product_id)
        order = get_object_or_404(Order, id=order_id)

        login_id= request.session.get("login_id")
        # if not login_id:
        #     HttpResponse('''<script>alert("you are not a buyer, please login ");window.location='/login/'</script>''')
        #     return redirect("login")

        login = get_object_or_404(Login, id=login_id)

        review, created = Review.objects.update_or_create(
            product=product,
            orders=order,
            login=login,
            defaults={
                "rating": rating,
                "comment": comment,
            }
        )
        review.save()
        
        
        return HttpResponse('''<script>alert("Review submitted ");window.location='/orders/'</script>''')

    return redirect("index")




# Buyer cart

def add_to_cart(request,product_id):
    login_id=request.session.get('lid')
    product=Product.objects.get(id=product_id)
    login=Login.objects.get(id=login_id)

    cart_item, created=Cart.objects.get_or_create(login=login,product=product,defaults={'quantity':1})
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')



def view_cart(request):
    cart = Cart.objects.filter(login_id=request.session['lid'])
    total = sum(i.quantity *(i.product.price) for i in cart)
    return render(request, 'cart.html', {'cart': cart, 'total': total})


def remove_from_cart(request,cart_id):
    cart=Cart.objects.get(id=cart_id).delete()
    return redirect('view_cart')

def checkout(request):
    cart = Cart.objects.filter(login_id=request.session['lid'])
    total = sum(i.quantity *(i.product.price) for i in cart)
    return render(request,'checkout.html',{'cart': cart, 'total': total})
  


def place_order(request):
    if request.method == "POST":
        login_id = request.session.get('lid')
        login = Login.objects.get(id=login_id)
        cart_items = Cart.objects.filter(login=login)

        fname = request.POST['fname']
        lname = request.POST['lname']
        address = request.POST['address']
        state = request.POST['state']
        email = request.POST['email']
        postal_code = request.POST['postal_code']
        phone = request.POST['phone']



        order = None
        total = 0
        for item in cart_items:
            total += item.quantity * item.product.price
            order = Order.objects.create(
                login=login,
                product=item.product,
                quantity=item.quantity,
                fname=fname,
                lname=lname,
                address=address,
                state=state,
                email=email,
                postal_code=postal_code,
                total_amount=item.quantity * item.product.price,
                phone=phone,
                payment_method="card",
                payment_status='Pending'
            )

        cart_items.delete()  

        return redirect('payment',order_id=order.id)
    else:
         return redirect('checkout')

from django.shortcuts import get_object_or_404

def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    callback_url = 'paymenthandler/'
    context = {
         "order": order,
         "amount": order.total_amount,
         "currency": "INR",
         "check_id": order.id,
         "callback_url": callback_url  # your Razorpay key
    }
    return render(request, "payment.html", context)


def payment_post(request):
     if request.method=="POST":
          order_id=request.POST.get("checkout_id")
          amount=request.POST.get("amount")
          razorpay_payment_id=request.POST.get("razorpay_payment_id")

          payment=Payment(
               amount=amount,
               razorpay_payment_id=razorpay_payment_id,
               checkout_id=order_id,
               date= datetime.now()
          )
          
        
     return HttpResponse('''<script>alert("Payment successful!");window.location="/thankyou/"</script>''')
          

def thankyou(request):
    return render(request,'thankyou.html')
















# checking functions

def check_is_seller(request):
    try:
        type=request.session['type']
        if type=='Seller':
            is_seller=True
        else:
            is_seller=False
        return is_seller
    except:
        return False
    
def check_is_buyer(request):
    try:
        type=request.session['type']
        print(type)
        if type == 'Buyer':
            is_buyer=True
        else:
            is_buyer=False
        return is_buyer    
    except:
        return False