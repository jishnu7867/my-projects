import datetime

from datetime import datetime
from django.utils import timezone 
from django.db import models

# Create your models here.


#Login 



class Login(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=300)
    salt = models.CharField(max_length=250)
    type = models.CharField(max_length=50)

# Sign up
class Signup(models.Model):
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=30)
    pincode = models.IntegerField()
    type = models.CharField(max_length=60)
    password = models.CharField(max_length=300)
    login = models.ForeignKey(Login,on_delete=models.CASCADE)
    p_image = models.ImageField(upload_to='profile_images/', default='profile_images/default-user.png')
    created_at= models.DateField(auto_now_add=True)

# Product
class Product(models.Model):
    signup=models.ForeignKey(Signup, on_delete=models.CASCADE)
    login=models.ForeignKey(Login, on_delete=models.CASCADE)
    title=models.CharField(max_length=200)
    category=models.CharField(
        max_length=50,
        choices=[
            ('dslr','DSLR Camera'),
            ('mirrorless','Mirrorless camera'),
            ('lens','Lens'),
            ('lighting','Lighting Equipment'),
            ('tripod','Trippod & Support'),
            ('audio','Audio Equipment'),
            ('accessory','Accessory'),
        ]
    )
    brand=models.CharField(
        max_length=50,
        choices=[
            ('canon','Canon'),
            ('nikon','Nikon'),
            ('sony','Sony'),
            ('panasonic','Panasonic'),
            ('sigma','Sigma'),
            ('fujifilm','Fujifilm'),
            ('tamron','Tamron'),
            ('other','Other')
        ]
    )
    model=models.CharField(max_length=100)
    condition=models.CharField(
        max_length=50,
        choices=[
            ('excellent','Excellent - Like new'),
            ('very-good','Very Good - Minor signs of use'),
            ('good', 'Good - Normal waer and tear'),
        ]
    )
    availability=models.CharField(
        max_length=50,
        choices=[
            ('available','Available'),
            ('unavailable','Currently Unavailable'),
        ]
    )
    description=models.TextField()
    daily_price=models.DecimalField(max_digits=10,decimal_places=2)
    weekly_price=models.DecimalField(max_digits=10,decimal_places=2, null=True,blank=True)
    monthly_price=models.DecimalField(max_digits=10,decimal_places=2, null=True,blank=True)
    security_deposit=models.DecimalField(max_digits=10,decimal_places=2,default=0)

    location = models.CharField(
        max_length=100,
        choices=[
            ('thiruvananthapuram','Thiruvananthapuram'),
            ('kollam','Kollam'),
            ('pathanamthitta','Pathanamthitta'),
            ('alappuzha','Alappuzha'),
            ('kottayam','Kottayam'),
            ('idukki','Idukki'),
            ('ernamkulam','Ernamkulam'),
            ('trissur','Trissur'),
            ('palakkad','Palakkad'),
            ('malappuram','Malappuram'),
            ('kozhikkode','Kozhikkode'),
            ('wayanad','Wayanad'),
            ('kannur','Kannur'),
            ('kasaragode','Kasaragode'),
        ]
     )



    pickup= models.BooleanField(default=True)
    shipping= models.BooleanField(default=False)
    meetup= models.BooleanField(default=False)
    delivery_fee= models.DecimalField(max_digits=10,decimal_places=2, default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='product_images/')

class ProductFeature(models.Model):
    product= models.ForeignKey(Product, on_delete=models.CASCADE, related_name="features")
    features=models.CharField(max_length=300)

class RenterMessage(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    signup=models.ForeignKey(Signup, on_delete=models.CASCADE)
    login=models.ForeignKey(Login, on_delete=models.CASCADE)
    name= models.CharField(max_length=100)
    email=models.EmailField()
    subject=models.CharField(max_length=200)
    message= models.TextField()
    created_at= models.DateField(auto_now_add=True)

class RentRequest(models.Model):
    product= models.ForeignKey(Product, on_delete=models.CASCADE)
    renter= models.ForeignKey(Signup,on_delete=models.CASCADE)
    from_date = models.DateField(default=timezone.now)  
    to_date = models.DateField(default=timezone.now) 
    rental_days = models.PositiveIntegerField(default=1)
    final_amount= models.DecimalField(max_digits=10, decimal_places=2,default=0)
    status=models.CharField(
        max_length=100,
        choices=[
            ('pending','Pedning'),
            ('accepted','Accepted'),
            ('rejected','Rejected'),
            ],
        default='pending'
    )
    created_at= models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Payment(models.Model):
    rent_request=models.ForeignKey('RentRequest',on_delete=models.CASCADE)
    amount=models.DecimalField(max_digits=10, decimal_places=2)
    date=models.DateTimeField(auto_now_add=True)