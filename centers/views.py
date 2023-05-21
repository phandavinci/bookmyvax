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
    return rows

def countvacancy():
    today = date.today()
    result = entries.objects.filter(date_field__date=today).values('id').annotate(count=Count('id'))
    for item in result:
        id_value = item['id']
        count = item['count']
        print(f"ID: {id_value}, Count: {count}")