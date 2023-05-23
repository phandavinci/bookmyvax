from django.db import models
from user.models import UserSignIn
import pytz
from django.utils import timezone
# Create your models here.

class centersdb(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    mobileno = models.CharField(max_length=10)
    line1 = models.CharField(max_length=50)
    line2 = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6)
    whfrom = models.CharField(max_length=8)
    whto = models.CharField(max_length=8)
    created = models.DateField(auto_now_add=True, verbose_name='EntryDateTime')
    def save(self, *args, **kwargs):
        tz = pytz.timezone('Asia/Kolkata')  # Set the desired timezone
        current_datetime = timezone.now().astimezone(tz)
        self.created = current_datetime
        super().save(*args, **kwargs)
    def __str__(self):
        return str(self.id)
    
class entries(models.Model):
    centerid = models.ForeignKey(centersdb, on_delete=models.CASCADE)
    userno = models.ForeignKey(UserSignIn, on_delete=models.CASCADE)
    entrydatetime = models.DateTimeField(auto_now_add=True, verbose_name='EntryDateTime')
    def save(self, *args, **kwargs):
        tz = pytz.timezone('Asia/Kolkata')  # Set the desired timezone
        current_datetime = timezone.now().astimezone(tz)
        self.entrydatetime = current_datetime
        super().save(*args, **kwargs)
    def __str__(self):
        return str(self.entrydatetime)
    
