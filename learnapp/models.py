from django.db import models
from django.contrib.auth.models import User
# Create your models here.
user_type=[
    ('USER','User'),
    ('VENDER','Vendor'),
]

class UserDetails(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)

    #additional fields
    phone=models.BigIntegerField()
    address=models.CharField(max_length=100)
    street=models.CharField(max_length=50)
    city=models.CharField(max_length=30)
    zipcode=models.CharField(max_length=50)
    userpic=models.ImageField(upload_to='userimg/',blank=True,null=True)
    user_type=models.CharField(max_length=10,choices=user_type,default='USER')



    

