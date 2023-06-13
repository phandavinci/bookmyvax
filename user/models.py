from django.db import models

# Create your models here.

class UserSignIn(models.Model):
    name = models.CharField(max_length=100)
    mobileno = models.CharField(max_length=10, primary_key=True)
    email = models.EmailField()
    password = models.CharField(max_length=46)
    cookiekey = models.CharField(max_length=45, default='0')
    age = models.CharField(max_length=2)
    gender = models.CharField(max_length=1)
    bloodgroup = models.CharField(max_length=3)
    # doorno = models.CharField(max_length=6, blank=True, null=True)
    # line1 = models.CharField(max_length=50, blank=True, null=True)
    # line2 = models.CharField(max_length=50, blank=True, null=True)
    # city = models.CharField(max_length=50)
    # pincode = models.CharField(max_length=6)
    created = models.DateTimeField(auto_now_add=True, verbose_name='EntryDateTime')
    def __str__(self) -> str:
        return self.name
    
class message(models.Model):
    users = models.ForeignKey(UserSignIn, on_delete=models.CASCADE)
    sub = models.TextField(null=True)
    message = models.TextField(null=True)
    is_read = models.BooleanField(default=False)
    entrydate = models.DateField(auto_now_add=True)