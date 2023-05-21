from django.db import models

# Create your models here.
class admindetails(models.Model):
    username = models.CharField(max_length=100, primary_key=True)
    mobileno = models.CharField(max_length=10)
    password = models.CharField(max_length=46)
    cookiekey = models.CharField(max_length=45, default='0')
    age = models.CharField(max_length=2)
    gender = models.CharField(max_length=1)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self) -> str:
        return self.username
    