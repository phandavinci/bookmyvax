from django.shortcuts import render
from django.db.models import Q
from .models import centersdb, entries
from django.db.models import Count
from datetime import date

# Create your views here.
def matchingrows(search_string):
    rows = centersdb.objects.filter(
        Q(id__icontains=search_string) |
        Q(mobileno__icontains=search_string) |
        Q(line1__icontains=search_string) |
        Q(line2__icontains=search_string) |
        Q(city__icontains=search_string) |
        Q(pincode__icontains=search_string) 
    )
    
    today = date.today()
    #count = entries.objects.filter(entrydatetime__date=today, centerid=rows.id)
    return rows
    
    