
from django.db import models
from django.utils import timezone
from django.utils.timezone import now




# Create your models here.

# login

class Login(models.Model):
    
    email=models.CharField(max_length=50)
    mobile=models.CharField(max_length=12)
    password=models.CharField(max_length=50)
    salt=models.CharField(max_length=50)
    type=models.CharField(max_length=20, default=1)

# seller

class Seller(models.Model):
    brand=models.CharField(max_length=50)
    owner=models.CharField(max_length=50)
    address=models.CharField(max_length=400)
    profile_picture=models.FileField(blank=True, null=True)
    email=models.CharField(max_length=100)
    mobile=models.CharField(max_length=12)
    password=models.CharField(max_length=50)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    bio=models.CharField(max_length=500,default=1)
    login=models.ForeignKey(Login,on_delete=models.CASCADE)



class Product(models.Model):
    title=models.CharField(max_length=100)
    category=models.CharField(max_length=100)
    sub_category=models.CharField(max_length=100)
    description=models.CharField(max_length=100)
    images=models.FileField(max_length=100)
    qty=models.IntegerField()
    dimensions=models.CharField(max_length=100)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    login=models.ForeignKey(Login,on_delete=models.CASCADE, default=1)
    
    

# buyer

class Buyer(models.Model):
    fname=models.CharField(max_length=50)
    lname=models.CharField(max_length=50)
    email=models.CharField(max_length=100)
    mobile=models.CharField(max_length=12)
    password=models.CharField(max_length=50)
    p_image=models.FileField( blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    login=models.ForeignKey(Login,on_delete=models.CASCADE)


class Purchase(models.Model):
    products=models.ForeignKey(Product,on_delete=models.CASCADE)
    seller_id=models.CharField(max_length=255,default="0")
    login=models.ForeignKey(Login,on_delete=models.CASCADE)
    name=models.CharField(max_length=50)
    phone1=models.CharField(max_length=15)
    phone2=models.CharField(max_length=15)
    shipping_address=models.CharField(max_length=250)
    state=models.CharField(max_length=20)
    city=models.CharField(max_length=20)
    pincode=models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True) 
    payment=models.CharField(max_length=20,choices=[('card','Debit/Credit Card'),('netbanking','UPI/Net Banking'),('banktransfer','Bank Transfer')])
    status=models.CharField(
        max_length=20,
        choices=[('purchase','purchase'),('purchased','Continue Purchase')],
        default='purchase'
        )


class Cart(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)
    login=models.ForeignKey(Login,on_delete=models.CASCADE)

class Index(models.Model):
    products=models.ForeignKey(Product,on_delete=models.CASCADE)
    buyer=models.ForeignKey(Buyer,on_delete=models.CASCADE)
    

class Order(models.Model):
    product=models.ForeignKey(Product,default=1, on_delete=models.CASCADE,related_name="order_product")
    quantity= models.IntegerField(default=1)
    login = models.ForeignKey(Login, on_delete=models.CASCADE)
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    address = models.TextField()
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method=models.CharField(
        max_length=20,
         choices=[('card','Debit/Credit Card'),('netbanking','UPI/Net Banking'),('banktransfer','Bank Transfer')],
         default='card')
    payment_status=models.CharField(
        max_length=20,
        choices=[('Pending','Pending'),('Initiated','Initiated'),('Completed','Completed')],
        default='Pending'
        )
    

class Payment(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(default=now)

   
class Review(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="reviews")
    orders=models.ForeignKey(Order,on_delete=models.CASCADE,related_name="order_reviews")
    login=models.ForeignKey(Login,on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    comment=models.TextField(blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
