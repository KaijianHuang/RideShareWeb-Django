from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField

class Rider(User):
    phone = models.BigIntegerField()
    def __str__(self):
        return f'Rider {self.user.username}'

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Brith = models.DateField()
    maxP = models.IntegerField()
    PlateNum = models.CharField(max_length=100)
    LicenseNum = models.CharField(max_length=100)
    Special = models.CharField(max_length=100)
    Color = models.CharField(max_length = 100)
    Vtype = models.CharField(max_length=100)
    Brand = models.CharField(max_length=100)
    Model = models.CharField(max_length=100)
    
    
    def __str__(self):
        return f'Driver {self.user.username}'

class RideDetail(models.Model):
    owner = models.CharField(max_length=200)
    OwnerEmail = models.CharField(max_length=200,default="kh492@duke.edu")
    driver = models.CharField(max_length=200, blank=True, null=True)
    sharable = models.BooleanField(default=False,blank=True,null=True)
    RemainSeats = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='Open')
    destination = models.CharField(max_length=200, blank=True, null=True)
    arrival_time = models.DateTimeField(default=timezone.now)
    Vtype = models.CharField(max_length=20, default='Sedan')
    Special = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.owner

class Ride(models.Model):
    user_role = models.CharField(max_length=20)
    party_size = models.IntegerField(default= 1)
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True,db_column='user')
    ride_detail = models.ForeignKey(RideDetail, on_delete=models.CASCADE,blank=True,null=True)

    def __str__(self):
        return self.owner