from django.contrib import admin

# Register your models here.
from .models import UserSignIn, message
admin.site.register(UserSignIn)
admin.site.register(message)