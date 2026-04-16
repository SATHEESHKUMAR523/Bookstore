from django.db import models

# Create your models here.

class Book(models.Model):
    title=models.CharField(max_length=225)
    author=models.CharField(max_length=225)
    price=models.DecimalField(max_digits=8,decimal_places=2)
    stock=models.PositiveIntegerField(default=0)
    image=models.ImageField(upload_to='books/', null=True, blank=True)


    def __str__(self):
        return self.title

class BestSeller(models.Model):
    book_name=models.CharField(max_length=225) 
    price=models.DecimalField(max_digits=8,decimal_places=2)  
    stock=models.IntegerField(default=0) 
    book_img=models.ImageField(upload_to='bestseller/',blank=True,null=True)    


class User(models.Model):
    username=models.CharField(max_length=225,unique=True)
    email=models.EmailField(unique=True)  
    password=models.CharField(max_length=222)
   

    def __str__(self):
        return self.username  

class Admin(models.Model):
    admin = models.EmailField()


class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)
    user_name = models.CharField(max_length=225)
    user_email = models.EmailField()
    amount = models.PositiveIntegerField()   # store in paise
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.amount} - {self.status}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name        