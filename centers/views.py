from django.shortcuts import render
from django.db.models import Q
from .models import centersdb, entries
from user.models import UserSignIn
from django.db.models import Count
from datetime import date

# Create your views here.

today = date.today()
def matchingrows(search_string):
    rows = centersdb.objects.filter(
        Q(name__icontains=search_string) |
        Q(id__icontains=search_string) |
        Q(mobileno__icontains=search_string) |
        Q(line1__icontains=search_string) |
        Q(line2__icontains=search_string) |
        Q(city__icontains=search_string) |
        Q(pincode__icontains=search_string) 
    )
    res = []
    for i in range(len(rows)):
        count = entries.objects.filter(Q(entrydate=today), centerid=rows[i].id)
        res.append(
                {'id':rows[i].id,
                'name':rows[i].name,
                'mobileno':rows[i].mobileno,
                'line1':rows[i].line1,
                'line2':rows[i].line2,
                'city':rows[i].city,
                'pincode':rows[i].pincode,
                'whfrom':rows[i].whfrom,
                'whto':rows[i].whto,
                'count': 10-count.count()}
                )
        # return [today, count[i].entrydatetime.date()]
        # count = entries.objects.filter(entrydatetime__date=today, centerid=rows[i].id)
        # rows[i]['count'] = count
    return res
    
def mybookingsfilter(cookie):
    rows = entries.objects.filter(Q(entrydate=today), userno=UserSignIn.objects.get(cookiekey=cookie).mobileno).order_by('-entrydate')
    return rows

def futurebookingfilter(cookie):
    rows = entries.objects.filter(Q(entrydate__gt=today), userno=UserSignIn.objects.get(cookiekey=cookie).mobileno).order_by('-entrydate')
    return rows

def slots(id):
    res = {}
    for i in range(2):
        rows = entries.objects.filter(Q(entrydate=today), centerid=id, slot=i)
        res[i] = 3-rows.count()
    rows = entries.objects.filter(Q(entrydate=today), centerid=id, slot=i)
    res[2] = 4-rows.count()
    return res