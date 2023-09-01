from django.contrib import admin

# Register your models here.
from .models import centersdb, entries
admin.site.register(centersdb)
admin.site.register(entries)