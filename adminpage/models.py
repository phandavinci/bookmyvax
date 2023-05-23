from django.db import models
import pytz
from django.utils import timezone
# Create your models here.
class admindetails(models.Model):
    username = models.CharField(max_length=100, primary_key=True)
    mobileno = models.CharField(max_length=10)
    password = models.CharField(max_length=46)
    cookiekey = models.CharField(max_length=45, default='0')
    age = models.CharField(max_length=2)
    gender = models.CharField(max_length=1)
    created = models.DateTimeField(auto_now_add=True, verbose_name='EntryDateTime')
    def save(self, *args, **kwargs):
        tz = pytz.timezone('Asia/Kolkata')  # Set the desired timezone
        current_datetime = timezone.now().astimezone(tz)
        self.created = current_datetime
        super().save(*args, **kwargs)
    def __str__(self) -> str:
        return self.username
    