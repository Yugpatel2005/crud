from django.db import models
from django.utils.safestring import mark_safe


# Create your models here.

class registermodel(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()
    phone = models.BigIntegerField()
    password = models.CharField(max_length=30)
    address = models.TextField()
    gender = models.CharField(max_length=30)
    role = models.CharField(max_length=10)
    profilepicture = models.ImageField(upload_to="photos")

    def user_photo(self):
        return mark_safe('<img src="{}" width="100"/>'.format(self.profilepicture.url))

    user_photo.allow_tags = True

    def __str__(self):
        return self.name

class category(models.Model):
    catname = models.CharField(max_length=30)

    def __str__(self):
        return self.catname

class product(models.Model):
    name = models.CharField(max_length=20)
    catid = models.ForeignKey(category,on_delete=models.CASCADE)
    pimage = models.ImageField(upload_to="photos")
    price = models.FloatField()
    description = models.TextField()
    status = models.CharField(max_length=20)
    sellerid = models.ForeignKey(registermodel,on_delete=models.CASCADE)

    def product_photo(self):
        return mark_safe('<img src="{}" width="100"/>'.format(self.pimage.url))

    product_photo.allow_tags = True

    def __str__(self):
        return self.name

class cart(models.Model):
    userid = models.ForeignKey(registermodel,on_delete=models.CASCADE)
    productid = models.ForeignKey(product,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    totalamount = models.FloatField()
    orderstatus = models.IntegerField() # 1 - added , 0-orderplace/remove
    orderid = models.IntegerField() # default - 0 , update orderid when user placed the order

class ordermodel(models.Model):
   userid = models.ForeignKey(registermodel, on_delete=models.CASCADE)
   finaltotal = models.FloatField()
   phone = models.BigIntegerField()
   address = models.TextField()
   paymode = models.CharField(max_length=40)
   timestamp = models.DateTimeField(auto_now_add=True)
   status = models.BooleanField(default=False)
   razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
