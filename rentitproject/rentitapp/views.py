import hashlib
from pyexpat.errors import messages
import random
from django.utils.timezone import now
import string
from decimal import Decimal
import datetime
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
import razorpay
from django.views.decorators.csrf import csrf_exempt

from rentitproject import settings
from .models import *

# Create your views here.


# Login

def login(request):
    return render(request,'login.html')

def login_post(request):
    email = request.POST['email']
    password = request.POST['password']

    log = Login.objects.filter(email=email).first()  # safe lookup
    if log:
        salt = log.salt  # use the same record
        password = password + salt
        password = hashlib.md5(password.encode('utf-8')).hexdigest()

        # Check password match
        if log.password == password:
            # store session details
            request.session['lid'] = log.id
            request.session['type'] = log.type

            # Link to Signup (if it exists)
            try:
                signup = Signup.objects.get(login=log)
                if log.type in ['lender', 'both']:
                    request.session['lender_id'] = signup.id
                if log.type in ['renter', 'both']:
                    request.session['renter_id'] = signup.id
            except Signup.DoesNotExist:
                pass  # ignore if signup not found

            # Redirect by type
            if log.type == "renter":
                return redirect('/index/')
            elif log.type == "lender":
                return redirect('/index/')
            elif log.type == "both":
                return redirect('/dashboard_both/')
            else:
                return HttpResponse('''<script>alert("Unknown account type.");window.location="/login/";</script>''')

        else:
            return HttpResponse('''<script>alert("Invalid password.");window.location="/login/";</script>''')
    else:
        return HttpResponse('''<script>alert("Invalid email.");window.location="/login/";</script>''')


# Signup

def register(request):
    log=Login.objects.all()
    return render(request,'register.html',{'log':log})

def register_post(request):
    if request.method=="POST":
        fname=request.POST['fname']
        lname=request.POST['lname']
        email= request.POST['email']
        phone= request.POST['phone']
        address=request.POST['address']
        city= request.POST['city']
        pincode= request.POST['pincode']
        type= request.POST['type']
        password=request.POST['password']
        confirm_password= request.POST['confirm_password']

        if password !=confirm_password:
            return HttpResponse('''<script>alert("Password do not match.!");window.location="/register/";</script>''')
        
        if Signup.objects.filter(email=email).exists():
            return HttpResponse('''<script>alert("An account with this Email or phone number already exists.!");window.location="/login/";</script>''')

        salt=''.join(random.choices(string.ascii_letters,k=7))
        password = password+salt
        password_hashed = hashlib.md5(password.encode('utf-8')).hexdigest()

        log = Login(email=email, password=password_hashed,salt=salt,type=type)  
        log.save()

        Signup.objects.create(
            fname=fname,
            lname=lname,
            email=email,
            phone=phone,
            address=address,
            city=city,
            pincode=pincode,
            type=type,
            password=password_hashed,
            login=log,
        )
        

        return HttpResponse('''<script>alert("Registration successfull.! Please login.");window.location="/login/";</script>''')

# index

def index(request):
    products = Product.objects.all()[:6]
    return render(request, 'index.html', {'products': products, 'year': now().year})

def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')


# Profile

def profile(request):
    if 'lid' not in request.session:
        return redirect('/login/')
    
    login_id = request.session['lid']
    user = Signup.objects.get(login_id=login_id)
    return render(request, 'profile.html', {'user': user})


def update_profile(request):
    if 'lid' not in request.session:
        return redirect('/login/')
    
    login_id = request.session['lid']
    user = Signup.objects.get(login_id=login_id)

    if request.method == 'POST':
        user.fname = request.POST['fname']
        user.lname = request.POST['lname']
        user.phone = request.POST['phone']
        user.address = request.POST['address']
        user.city = request.POST['city']
        user.pincode = request.POST['pincode']

        if 'p_image' in request.FILES:
            user.p_image = request.FILES['p_image']

        user.save()
        return HttpResponse('<script>alert("Profile updated successfully!");window.location="/profile/";</script>')

    return render(request, 'profile.html', {'user': user})



# dashboard_both

def dashboard_both(request, request_id=None):

    user_type = request.session.get('user_type')
    lender_id = request.session.get('lender_id')
    renter_id = request.session.get('renter_id')

    # lender side
    requests = RentRequest.objects.filter(product__signup_id=lender_id).order_by('-created_at') if lender_id else RentRequest.objects.none()

    selected_request = None
    if request_id:
        selected_request = requests.filter(id=request_id).first()

    my_listings = Product.objects.filter(signup_id=lender_id) if lender_id else Product.objects.none()
    active_rentals = requests.filter(status='accepted') if lender_id else RentRequest.objects.none()

    # renter side
    rentals = RentRequest.objects.filter(renter_id=renter_id).select_related('product').order_by('-created_at') if renter_id else RentRequest.objects.none()

    return render(
        request,
        'dashboard(both).html',
        {   
            'user_type': user_type,
            'requests': requests,
            'selected_request': selected_request,
            'my_listings': my_listings,
            'active_rentals': active_rentals,
            'rentals': rentals,
        }
    )





# item upload
def product_upload(request):
    if 'lid' in request.session:
        return render(request, 'product_upload.html')
    else:
        return HttpResponse('''<script>alert("Please login first.");window.location="/login/";</script>''')


def product_upload_post(request):
    if request.method == "POST":
        if 'lid' not in request.session:
            return HttpResponse('''<script>alert("Please login first.");window.location="/login/";</script>''')

        user_id = request.session.get('lid')

        # Get user (Signup record)
        try:
            user = Signup.objects.get(login_id=user_id)
        except Signup.DoesNotExist:
            return HttpResponse('''<script>alert("User account not found. Please register.");window.location="/register/";</script>''')



        title=request.POST['title']
        category=request.POST['category']
        brand=request.POST['brand']
        model=request.POST['model']
        condition=request.POST['condition']
        availability=request.POST['availability']
        description=request.POST['description']
        daily_price=request.POST['daily_price']
        weekly_price=request.POST['weekly_price']
        monthly_price=request.POST['monthly_price']
        location=request.POST['location']
        pickup= True if request.POST['pickup'] else False
        shipping= True if request.POST['shipping'] else False
        meetup= True if request.POST['meetup'] else False
        delivery_fee=request.POST['delivery_fee']

        login_id=request.session['lid']

        product=Product(
            signup=user,
            title=title,
            category=category,
            brand=brand,
            model=model,
            condition=condition,
            availability=availability,
            description=description,
            daily_price=daily_price,
            weekly_price=weekly_price,
            monthly_price=monthly_price,
            location=location,
            pickup=pickup,
            shipping=shipping,
            meetup=meetup,
            delivery_fee=delivery_fee,
            login_id=login_id
            )
        product.save()

        # features
        features= request.POST.getlist('features[]')
        for f in features:
            if f.strip():
                ProductFeature.objects.create(product=product, features=f.strip())


        # images
        if request.FILES.getlist("images"):
            images = request.FILES.getlist('images')
            for img in images:
                ProductImage.objects.create(product=product, image=img)
        return HttpResponse('''<script>alert("Product added successfully");window.location="/product_list/";</script>''')
    

        

def product_edit(request, id):
    product = Product.objects.get(id=id)
    images = ProductImage.objects.filter(product=product)
    features = ProductFeature.objects.filter(product=product)
    return render(request, 'product_edit.html', {'product': product, 'images': images, 'features': features})


def product_edit_post(request, id):
    product = Product.objects.get(id=id)

    if request.method == 'POST':
        # Update product fields
        product.title = request.POST['title']
        product.category = request.POST['category']
        product.brand = request.POST['brand']
        product.model = request.POST['model']
        product.condition = request.POST['condition']
        product.availability=request.POST['availability']
        product.description = request.POST['description']
        product.daily_price = request.POST['daily_price']
        product.weekly_price = request.POST.get('weekly_price', 0)
        product.monthly_price = request.POST.get('monthly_price', 0)
        product.security_deposit = request.POST['security_deposit']
        product.location = request.POST.get('location', product.location)
        product.pickup = 'pickup' in request.POST
        product.shipping = 'shipping' in request.POST
        product.meetup = 'meetup' in request.POST
        product.delivery_fee = request.POST['delivery_fee']
        product.save()

        # ✅ Update features only if changed
        features = [f.strip() for f in request.POST.getlist('features[]') if f.strip()]
        existing_features = list(ProductFeature.objects.filter(product=product).values_list('features', flat=True))
        if sorted(existing_features) != sorted(features):
            ProductFeature.objects.filter(product=product).delete()
            for f in features:
                ProductFeature.objects.create(product=product, features=f)

        # ✅ Update images (add new ones only)
        if request.FILES.getlist('images'):
            for img in request.FILES.getlist('images'):
                ProductImage.objects.create(product=product, image=img)

        return HttpResponse('''<script>alert("Product updated successfully");window.location="/product_list/";</script>''')

    return render(request, 'product_edit.html', {
        'product': product,
        'images': ProductImage.objects.filter(product=product),
        'features': ProductFeature.objects.filter(product=product),
    })





def product_delete(requset,id):
    product=Product.objects.get(id=id)
    images=ProductImage.objects.filter(product=product)
    for img in images:
        img.image.delete(save=False)
        img.delete()

    product.delete()
    return HttpResponse('''<script>alert("Product deleted successfully");window.location="/product_list/"</script>''')

def product_list(request):
    if 'lid' not in request.session:
        return HttpResponse('''<script>alert("Please login first.");window.location="/login/";</script>''')

    user_id = request.session.get('lid')

    try:
        user = Signup.objects.get(login_id=user_id)
    except Signup.DoesNotExist:
        return HttpResponse('''<script>alert("User account not found. Please register.");window.location="/register/";</script>''')

    products = Product.objects.filter(signup=user).order_by('-id')

    return render(request, 'product_list.html', {'products': products})


def single_product(request,id):
    product= Product.objects.get(id=id)
    features = ProductFeature.objects.filter(product=product)
    
    return render (request,'single_product.html',{'product':product,'features':features})


# All Products
def all_products(request):
    # Base queryset with prefetch for images and features
    products = Product.objects.all().prefetch_related('images', 'features')

    # Get filter parameters
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    location = request.GET.get('location')
    availability= request.GET.get('availability')
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Apply filters dynamically
    if category:
        products = products.filter(category__iexact=category)
    if brand:
        products = products.filter(brand__iexact=brand)
    if location:
        products = products.filter(location__icontains=location)
    if availability:
        products = products.filter(availability__icontains=availability)
    if min_price:
        products = products.filter(daily_price__gte=min_price)
    if max_price:
        products = products.filter(daily_price__lte=max_price)

    # Count for UI display
    count = products.count()

    return render(request, 'browse.html', {
        'products': products,
        'count': count,
    })

def search_product(request):
    if request.method == 'POST':
        search = request.POST['search']
        products = Product.objects.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(model__icontains=search) |
            Q(brand__icontains=search) |
            Q(category__icontains=search)
            # Q(features__name__icontains=search)
        ).distinct()

        return render(request, 'browse.html', {
            'products': products,
            'search': search,
            'count': products.count(),
        })

def product(request):
    products=Product.objects.filter(category="dslr")
    return render(request,'cam.html',{'products':products})
    
def product_single(request, id):
    product = get_object_or_404(Product, id=id)
    related_products = Product.objects.filter(category=product.category).exclude(id=id)[:3]
    images = ProductImage.objects.filter(product=product)
    features = ProductFeature.objects.filter(product=product)
    reviews = Review.objects.filter(product=product).order_by('-created_at')

    # Handle new review submission
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if name and email and rating and comment:
            Review.objects.create(
                product=product,
                name=name,
                email=email,
                rating=int(rating),
                comment=comment
            )
            return redirect('product_single', id=product.id) 

    return render(request, 'car-single.html', {
        'product': product,
        'related_products': related_products,
        'images': images,
        'features': features,
        'reviews': reviews,
    })

# contact lender
def contact_lender(request, product_id):
    product = Product.objects.get(id=product_id)
    lender = product.signup  

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        login_id = request.session.get('login_id')
        signup_obj = Signup.objects.filter(login_id=login_id).first()

        if not signup_obj:
            messages.error(request, "Please log in to send a message.")
            return redirect('/login/')

        RenterMessage.objects.create(
            product=product,
            signup=signup_obj,
            login=signup_obj.login,
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        messages.success(request, "Your message has been sent to the lender.")
        return redirect(f'/contact_lender/{product.id}/')

    previous_messages = RenterMessage.objects.filter(
        product=product,
        signup__login_id=request.session.get('login_id')
    ).order_by('-created_at')

    return render(request, 'contact_lender.html', {
        'product': product,
        'lender': lender,
        'previous_messages': previous_messages
    })
    
    

# Request

def renter_request(request, product_id):
    if 'lid' not in request.session:
        return HttpResponse('''<script>alert("Please login!."); window.location="/login/";</script>''')

    user_id = request.session['lid']
    product = get_object_or_404(Product, id=product_id)
    renter = get_object_or_404(Signup, login_id=user_id)

    if request.method == "POST":
        from_date_str = request.POST.get('from_date')
        to_date_str = request.POST.get('to_date')

        if not from_date_str or not to_date_str:
            return HttpResponse('''<script>alert("Please select both From and To dates."); window.history.back();</script>''')

        # Convert string dates to datetime objects
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()

        if to_date < from_date:
            return HttpResponse('''<script>alert("To date cannot be earlier than From date."); window.history.back();</script>''')

        # Calculate rental days
        rental_days = (to_date - from_date).days + 1  

        #base amount
        daily_price = Decimal(product.daily_price)
        amount= rental_days*Decimal(rental_days)


        if rental_days <= 6:
            final_amount= amount
        elif 7<= rental_days < 24:
            off_amount= amount* Decimal('0.10')   #10% off
            final_amount= amount-off_amount 
        else:
            off_amount= amount* Decimal('0.25')    #25% off
            final_amount= amount-off_amount

        # Optional: create a RenterRequest object or booking
        rent_request= RentRequest(
            product=product,
            renter=renter,
            from_date=from_date,
            to_date=to_date,
            rental_days=rental_days,
            final_amount=final_amount,
            status='pending'  # or whatever default
        )
        rent_request.save()

        return HttpResponse('''<script>alert("Booking request sent successfully."); window.location="/#/";</script>''')

    return render(request, 'product_detail.html', {'product': product, 'renter': renter})


razorpay_api_key = settings.RAZORPAY_API_KEY
razorpay_secret_key = settings.RAZORPAY_API_SECRET
razorpay_client = razorpay.Client(auth=(razorpay_api_key, razorpay_secret_key))

@csrf_exempt
def payment(request, request_id):
    product = get_object_or_404(RentRequest, pk=request_id)

    # Convert to paisa
    amount = int(product.final_amount )
    print(amount);
    # Enforce minimum order amount
    if amount < 100:
        return HttpResponse(
            '''<script>alert("Minimum payment amount should be ₹1."); window.history.back();</script>'''
        )

    order_data = {
        'amount': amount,
        'currency': 'INR',
        'receipt': f'order_rcptid_{request_id}',
        'payment_capture': '1',
    }

    order = razorpay_client.order.create(data=order_data)

    context = {
        'razorpay_api_key': razorpay_api_key,
        'amount': amount,
        'currency': order_data['currency'],
        'order_id': order['id'],
        'request_id': request_id,
        'callback_url': 'paymenthandler/',
    }
    return render(request, 'payment.html', context)

# def payment(request,request_id):
#     product= get_object_or_404(RentRequest, pk=request_id)
#     # Amount to be paid (in paisa), you can change this dynamically based on your logic
#     amount = int(product.final_amount*100)
#     # Create a Razorpay order (you need to implement this based on your logic)
#     order_data = {
#         'amount': amount,
#         'currency': 'INR',
#         'receipt': 'order_rcptid_11',
#         'payment_capture': '1', # Auto-capture payment
#     }
#     # Create an order
#     order = razorpay_client.order.create(data=order_data)
#     print(order)
#     callback_url = 'paymenthandler/'
#     context = {
#         'razorpay_api_key': razorpay_api_key,
#         'amount': amount,
#         'currency': order_data['currency'],
#         'order_id': order['id'],
#         'request_id':request_id,
#         'callback_url':callback_url
#     }
#     return render(request, 'payment.html', context)

def payment_post(request):
    amount = request.POST['amount']
    request_id = request.POST['request_id']
    payment = Payment(
        amount=amount,
        request_id=request_id,
        date = datetime.now()
    )
    cc=renter_request.objects.get(id=request_id)
    cc.payment_status= 'Completed'
    cc.save()
    payment.save()


    return HttpResponse('''<script>alert("Payment successfull! Thanks for Shopping with us!");window.location="/orders_history/"</script>''')

  
# request status update
def update_rent_request_status(request, request_id, action):
    
    user_id = request.session['lid']
    user = get_object_or_404(Signup, login_id=user_id)
    rent_request =RentRequest.objects.get(id=request_id)

    # Verify that the logged-in user owns the product
    if rent_request.product.signup != user:
        return HttpResponse('''<script>alert("Unauthorized action!"); window.location="/";</script>''')

    if action == 'accept':
        rent_request.status = 'accepted'
    elif action == 'reject':
        rent_request.status = 'rejected'
    else:
        return HttpResponse('''<script>alert("Invalid action!");window.location="/";</script>''')

    rent_request.save()

    return HttpResponse(f'''<script>alert("Request {rent_request.status}!");window.location="#";</script>''')



# view requests

def request_view_lender(request, request_id=None):
    # Check that user is logged in 
    if 'lid' not in request.session:
        return HttpResponse(
            '''<script>alert("Please login first."); window.location="/login/";</script>'''
        )

    user_id = request.session['lid']

    #  Get the actual saved Signup instance
    user = Signup.objects.get(login_id=user_id)

    #  Get all rent requests for products owned by this lender
    requests = RentRequest.objects.filter(product__signup_id=user).order_by('-created_at')

    #  If a specific request ID is provided, get it safely
    selected_request = None
    if request_id:
        selected_request = RentRequest.objects.filter(id=request_id, product__signup_id=user).first()

    # Get all products by this user
    my_listings = Product.objects.filter(signup_id=user)

    #  Active rentals
    active_rentals = requests.filter(status='accepted')



    return render(
        request,
        'request_view_lender.html',
        {
            'requests': requests,
            'selected_request': selected_request,
            'my_listings': my_listings,
            'active_rentals': active_rentals,
        }
    )

#  Approve a rental request
def approve_request(request, req_id):
    rent_request = get_object_or_404(RentRequest, id=req_id)
    rent_request.status = 'accepted'
    rent_request.save()
    return HttpResponse('''<script>alert("Request approved!");window.location="/request_view_lender/";</script>''')


#  Reject a rental request
def reject_request(request, req_id):
    rent_request = get_object_or_404(RentRequest, id=req_id)
    rent_request.status = 'rejected'
    rent_request.save()
    return HttpResponse('''<script>alert("Request rejected!");window.location="/request_view_lender/";</script>''')


def proceed_to_payment(request, request_id):
    rent_request = RentRequest.objects.get(id=request_id)
    return render(request, 'proceed_to_payment.html', {'rent_request': rent_request})





# Condition

def check_is_renter(request):
    try:
        user_type = request.session['type']
        if user_type == 'renter' or user_type == 'both':
            return True
        else:
            return False
    except KeyError:
        return False


def check_is_lender(request):
    try:
        user_type = request.session['type']
        if user_type == 'lender' or user_type == 'both':
            return True
        else:
            return False
    except KeyError:
        return False    
    
def check_is_both(request):
    try:
        user_type= request.session['type']
        if user_type== 'both':
            return True
        else:
            return False
    except KeyError:
        return False