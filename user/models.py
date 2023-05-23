from django.db import models
import pytz
from django.utils import timezone

# Create your models here.

class UserSignIn(models.Model):
    name = models.CharField(max_length=100)
    mobileno = models.CharField(max_length=10, primary_key=True)
    password = models.CharField(max_length=46)
    cookiekey = models.CharField(max_length=45, default='0')
    age = models.CharField(max_length=2)
    gender = models.CharField(max_length=1)
    bloodgroup = models.CharField(max_length=3)
    doorno = models.CharField(max_length=6, blank=True, null=True)
    line1 = models.CharField(max_length=50, blank=True, null=True)
    line2 = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6)
    created = models.DateTimeField(auto_now_add=True, verbose_name='EntryDateTime')
    def save(self, *args, **kwargs):
        tz = pytz.timezone('Asia/Kolkata')  # Set the desired timezone
        current_datetime = timezone.now().astimezone(tz)
        self.created = current_datetime
        super().save(*args, **kwargs)
    def __str__(self) -> str:
        return self.name
    