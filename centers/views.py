from django.shortcuts import render
from django.http import HttpResponse
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
    
def slots(id, d):
    row = centersdb.objects.get(id=id)
    vacancy = row.vacancy
    slotno = row.slots
    whfrom = datetime.combine(d, row.whfrom)
    whto = datetime.combine(d, row.whto)
    total = abs((whfrom - whto)/slotno)
    a = vacancy // slotno
    result = [a] * slotno
    result[:vacancy % slotno] = [count + 1 for count in result[:vacancy % slotno]]
    res = []
    s = whfrom - total; e = whfrom
    for i, n in enumerate(result):
        s += total
        e = s+total if s+total<whto else whto
        n-= entries.objects.filter(centerid=id, slot=i, entrydate=d).count()
        if datetime.now()<=s+(total//4):
            res.append({'slot':i, 'rem':n, 'startime':s.time(), 'endtime':e.time()})
    return res    
    
def slot(row):
        slotno = row.centerid.slots
        is_vaccinated = row.is_vaccinated
        whfrom = datetime.combine(row.entrydate, row.centerid.whfrom)
        whto =  datetime.combine(row.entrydate, row.centerid.whto)
        total = abs((whfrom - whto)/slotno)
        fr = row.slot*total+datetime.combine(row.entrydate,row.centerid.whfrom)
        to = fr+total if fr+total<whto else whto
        if datetime.now() < fr+(total//2) and is_vaccinated==False:
            cancel = 1 
        elif is_vaccinated:
            cancel = 2
        else:
            cancel = 0
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

def vaccinatedbookings(cookie):
    rows = entries.objects.filter(userno=UserSignIn.objects.get(cookiekey=cookie).mobileno, is_vaccinated=True).order_by('-entrydate')
    for row in rows:
        row.slot = slot(row)
    return rows

def bookednotvaccinated(cookie):
    rows = entries.objects.filter(userno=UserSignIn.objects.get(cookiekey=cookie).mobileno, is_vaccinated=False, entrydate__lt=date.today()).order_by('-entrydate')
    for row in rows:
        row.slot = slot(row)
    return rows