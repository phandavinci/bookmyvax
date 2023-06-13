from django.shortcuts import render
from django.db.models import Q
from .models import centersdb, entries
from user.models import UserSignIn
from django.db.models import Count
from datetime import date, datetime, timedelta

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
    return rows
    
def slot(row):
        slotss = row.centerid.slots
        whfrom = datetime.combine(row.entrydate, row.centerid.whfrom)
        whto = datetime.combine(row.entrydate, row.centerid.whto)
        total = abs((whfrom - whto)/slotss)
        fr = row.slot*total+datetime.combine(row.entrydate,row.centerid.whfrom)
        to = fr+total if fr+total<whto else whto
        cancel = 1 if datetime.now() < fr+(total//2) else 0
        res = {'f':fr.time(), 't':to.time(), 'cancel':cancel}
        return res
    
def mybookingsfilter(cookie):
    rows = entries.objects.filter(Q(entrydate=today), userno=UserSignIn.objects.get(cookiekey=cookie).mobileno).order_by('-entrydate')
    for row in rows:
        row.slot = slot(row)
    return rows

def futurebookingfilter(cookie):
    rows = entries.objects.filter(Q(entrydate__gt=today), userno=UserSignIn.objects.get(cookiekey=cookie).mobileno).order_by('-entrydate')
    for row in rows:
        row.slot = slot(row)
    return rows

def allbookingfilter(cookie):
    rows = entries.objects.filter(userno=UserSignIn.objects.get(cookiekey=cookie).mobileno).order_by('-entrydate')
    for row in rows:
        row.slot = slot(row)
    return rows

def slots(id, d):
    row = centersdb.objects.get(id=id)
    vacancy = row.vacancy
    slotss = row.slots
    whfrom = datetime.combine(d, row.whfrom)
    whto = datetime.combine(d, row.whto)
    total = abs((whfrom - whto)/slotss)
    a = vacancy // slotss
    result = [a] * slotss
    result[:vacancy % slotss] = [count + 1 for count in result[:vacancy % slotss]]
    res = []; s = whfrom - total; e = whfrom
    for i, n in enumerate(result):
        s += total
        e = s+total if s+total<whto else whto
        n-= entries.objects.filter(centerid=id, slot=i, entrydate=d).count()
        if datetime.now()<=s+(total//4):
            res.append({'slot':i, 'rem':n, 'startime':s.time(), 'endtime':e.time()})
    return res